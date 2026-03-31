import argparse
import base64
import hashlib
import os
import re
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests

from db_config import DB_SCHEMA, get_connection
from app_pages.llm_interface import OllamaChat


OUTPUT_WIDTH = 800
OUTPUT_HEIGHT = 450
DEFAULT_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_IMAGE_ENDPOINT = os.getenv("OPENAI_IMAGE_ENDPOINT", "https://api.openai.com/v1/images/generations")
PROMPT_VERSION = "nanobanana-v2"

TEAM_STYLE_GUIDE = {
    "hawks": ("Atlanta Hawks", "red and yellow", "red home uniform with yellow trim"),
    "celtics": ("Boston Celtics", "green and white", "green home uniform with white trim"),
    "nets": ("Brooklyn Nets", "black and white", "black statement uniform with white trim"),
    "hornets": ("Charlotte Hornets", "teal and purple", "teal home uniform with purple trim"),
    "bulls": ("Chicago Bulls", "red, black, and white", "red home uniform with black trim"),
    "cavaliers": ("Cleveland Cavaliers", "wine and gold", "wine uniform with gold trim"),
    "mavericks": ("Dallas Mavericks", "navy and silver", "navy uniform with silver trim"),
    "nuggets": ("Denver Nuggets", "navy and gold", "navy uniform with gold trim"),
    "pistons": ("Detroit Pistons", "blue and red", "blue home uniform with red trim"),
    "warriors": ("Golden State Warriors", "blue and gold", "blue home uniform with gold trim"),
    "rockets": ("Houston Rockets", "red and black", "red home uniform with black trim"),
    "pacers": ("Indiana Pacers", "navy and gold", "navy uniform with gold trim"),
    "clippers": ("LA Clippers", "navy, red, and white", "navy uniform with red trim"),
    "lakers": ("Los Angeles Lakers", "purple and gold", "gold home uniform with purple trim"),
    "grizzlies": ("Memphis Grizzlies", "navy and light blue", "navy uniform with light blue trim"),
    "heat": ("Miami Heat", "black and red", "black uniform with red trim"),
    "bucks": ("Milwaukee Bucks", "green and cream", "green home uniform with cream trim"),
    "timberwolves": ("Minnesota Timberwolves", "navy, green, and white", "navy uniform with green trim"),
    "pelicans": ("New Orleans Pelicans", "navy, red, and gold", "navy uniform with gold trim"),
    "knicks": ("New York Knicks", "blue and orange", "blue home uniform with orange trim"),
    "thunder": ("Oklahoma City Thunder", "blue and orange", "blue uniform with orange trim"),
    "magic": ("Orlando Magic", "blue, black, and silver", "blue uniform with black trim"),
    "76ers": ("Philadelphia 76ers", "blue, red, and white", "blue home uniform with red trim"),
    "suns": ("Phoenix Suns", "purple and orange", "purple uniform with orange trim"),
    "blazers": ("Portland Trail Blazers", "black, red, and white", "black uniform with red trim"),
    "kings": ("Sacramento Kings", "purple and silver", "purple uniform with silver trim"),
    "spurs": ("San Antonio Spurs", "black and silver", "black uniform with silver trim"),
    "raptors": ("Toronto Raptors", "black and red", "black uniform with red trim"),
    "jazz": ("Utah Jazz", "yellow, black, and white", "yellow uniform with black trim"),
    "wizards": ("Washington Wizards", "red, white, and blue", "red uniform with navy trim"),
}

TEAM_ALIASES = {
    "atlanta": "hawks",
    "hawks": "hawks",
    "boston": "celtics",
    "celtics": "celtics",
    "brooklyn": "nets",
    "nets": "nets",
    "charlotte": "hornets",
    "hornets": "hornets",
    "chicago": "bulls",
    "bulls": "bulls",
    "cleveland": "cavaliers",
    "cavs": "cavaliers",
    "cavaliers": "cavaliers",
    "dallas": "mavericks",
    "mavs": "mavericks",
    "mavericks": "mavericks",
    "denver": "nuggets",
    "nuggets": "nuggets",
    "detroit": "pistons",
    "pistons": "pistons",
    "golden state": "warriors",
    "warriors": "warriors",
    "houston": "rockets",
    "rockets": "rockets",
    "indiana": "pacers",
    "pacers": "pacers",
    "clippers": "clippers",
    "la clippers": "clippers",
    "los angeles clippers": "clippers",
    "lakers": "lakers",
    "la lakers": "lakers",
    "los angeles lakers": "lakers",
    "memphis": "grizzlies",
    "grizzlies": "grizzlies",
    "miami": "heat",
    "heat": "heat",
    "milwaukee": "bucks",
    "bucks": "bucks",
    "minnesota": "timberwolves",
    "wolves": "timberwolves",
    "timberwolves": "timberwolves",
    "new orleans": "pelicans",
    "pelicans": "pelicans",
    "new york": "knicks",
    "knicks": "knicks",
    "oklahoma city": "thunder",
    "okc": "thunder",
    "thunder": "thunder",
    "orlando": "magic",
    "magic": "magic",
    "philadelphia": "76ers",
    "sixers": "76ers",
    "76ers": "76ers",
    "phoenix": "suns",
    "suns": "suns",
    "portland": "blazers",
    "trail blazers": "blazers",
    "blazers": "blazers",
    "sacramento": "kings",
    "kings": "kings",
    "san antonio": "spurs",
    "spurs": "spurs",
    "toronto": "raptors",
    "raptors": "raptors",
    "utah": "jazz",
    "jazz": "jazz",
    "washington": "wizards",
    "wizards": "wizards",
}

COMMON_NON_PLAYER_WORDS = {
    "NBA", "News", "Injury", "Game", "Games", "Playoffs", "Playoff", "Finals", "Season", "Report",
    "Reports", "Update", "Preview", "Recap", "Takeaways", "Takeaway", "Trade", "Deadline", "Draft",
    "Coach", "Coaches", "Team", "Teams", "League", "Today", "Tonight", "Against", "With", "From",
}


def normalize_whitespace(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


def extract_detected_teams(text):
    lowered = normalize_whitespace(text).lower()
    found = []
    for alias, canonical in TEAM_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", lowered):
            if canonical not in found:
                found.append(canonical)
    return found[:2]


def extract_player_candidates(title, content):
    combined = f"{title}. {content[:500]}"
    names = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b", combined)
    players = []
    for name in names:
        if any(token in COMMON_NON_PLAYER_WORDS for token in name.split()):
            continue
        if name not in players:
            players.append(name)
    return players[:3]


def extract_story_signals(title, content):
    text = f"{title} {content}".lower()
    action_map = [
        ("injury", "capturing a tense injury-update moment on the sideline"),
        ("return", "showing a dramatic return-to-action scene during warmups"),
        ("trade", "staging a media-day style portrait that hints at a roster move"),
        ("sign", "showing a posed introductory press conference moment"),
        ("waive", "framing a somber roster-shakeup media scrum"),
        ("coach", "showing a courtside coaching moment with strategy intensity"),
        ("preview", "capturing pregame anticipation moments before tipoff"),
        ("recap", "showing a decisive in-game highlight from the featured matchup"),
        ("buzzer", "freezing the instant after a dramatic late-game shot"),
        ("game-winner", "freezing the instant after a dramatic late-game shot"),
        ("overtime", "capturing exhausted players in a high-pressure late-game sequence"),
        ("playoffs", "showing a postseason atmosphere with heightened crowd tension"),
        ("finals", "showing a championship-stage atmosphere with elite intensity"),
    ]
    mood_map = [
        ("injury", "concerned and resilient"),
        ("return", "determined and energized"),
        ("trade", "focused and reflective"),
        ("sign", "proud and optimistic"),
        ("waive", "serious and restrained"),
        ("recap", "explosive and competitive"),
        ("preview", "locked-in and anticipatory"),
        ("playoffs", "desperate and intense"),
        ("finals", "epic and emotionally charged"),
    ]

    action = "showing a decisive in-game NBA moment tied directly to the article"
    mood = "intense focus"

    for keyword, mapped in action_map:
        if keyword in text:
            action = mapped
            break

    for keyword, mapped in mood_map:
        if keyword in text:
            mood = mapped
            break

    return action, mood


def build_prompt_facts(title, content, news_id=None):
    cleaned_title = normalize_whitespace(title)
    cleaned_content = normalize_whitespace(content)
    teams = extract_detected_teams(f"{cleaned_title} {cleaned_content}")
    team_details = [TEAM_STYLE_GUIDE[t] for t in teams if t in TEAM_STYLE_GUIDE]
    players = extract_player_candidates(cleaned_title, cleaned_content)
    action, mood = extract_story_signals(cleaned_title, cleaned_content)
    article_fingerprint = hashlib.sha256(f"{cleaned_title}|{cleaned_content[:1000]}".encode("utf-8")).hexdigest()[:10]

    if team_details:
        uniform_notes = " vs. ".join(detail[2] for detail in team_details)
        color_notes = " vs. ".join(detail[1] for detail in team_details)
        team_names = " vs. ".join(detail[0] for detail in team_details)
    else:
        uniform_notes = "modern NBA uniforms with distinct home and away color contrast"
        color_notes = "bold arena-ready colors"
        team_names = "an NBA matchup"

    primary_subject = players[0] if players else "a star NBA player"
    supporting_subject = players[1] if len(players) > 1 else "teammates and defenders"
    headline_context = cleaned_title[:160]
    content_context = cleaned_content[:320]

    return {
        "teams": team_names,
        "uniform_notes": uniform_notes,
        "color_notes": color_notes,
        "players": players,
        "primary_subject": primary_subject,
        "supporting_subject": supporting_subject,
        "action": action,
        "mood": mood,
        "headline_context": headline_context,
        "content_context": content_context,
        "article_fingerprint": article_fingerprint,
        "news_id": news_id,
    }


def build_fallback_prompt(title, content, news_id=None):
    facts = build_prompt_facts(title, content, news_id=news_id)
    unique_marker = f"story marker {facts['article_fingerprint']}"
    return normalize_whitespace(
        f"Create a unique photorealistic editorial NBA news image inspired by this article headline: "
        f"'{facts['headline_context']}'. Feature {facts['primary_subject']} with {facts['supporting_subject']}, "
        f"{facts['action']}. Use {facts['uniform_notes']}, body types appropriate for elite professional basketball players, "
        f"expressive faces with {facts['mood']}, sweat, motion blur, arena crowd, scoreboard glow, and realistic skin detail. "
        f"Composition should be a dynamic courtside camera angle with cinematic sports lighting, sharp focus on the featured subject, "
        f"natural depth of field, and colors matching {facts['color_notes']}. Avoid text overlays, avoid logos, avoid watermarks, "
        f"avoid collage layouts, avoid animals, avoid cats, avoid statues, avoid sculptures, avoid mascots, avoid toys, avoid figurines. "
        f"Capture the story context from: {facts['content_context']}. Ensure this frame is visually distinct and tied to {facts['teams']}. "
        f"Use {unique_marker} to make the composition different from other articles."
    )


def clean_generated_prompt(prompt):
    cleaned = normalize_whitespace(prompt)
    cleaned = cleaned.strip("\"'`")
    cleaned = re.sub(r"^(Prompt:)\s*", "", cleaned, flags=re.IGNORECASE)
    return cleaned


def preprocess_image_prompt(title, content, news_id=None):
    """Generate a detailed, article-specific image prompt."""
    fallback_prompt = build_fallback_prompt(title, content, news_id=news_id)
    llm = OllamaChat()
    if not llm.is_available:
        return fallback_prompt

    facts = build_prompt_facts(title, content, news_id=news_id)
    system_prompt = (
        "You write production-ready prompts for photorealistic NBA editorial image generation. "
        "Return exactly one detailed prompt between 90 and 150 words. "
        "Every prompt must be unique to the article and must clearly describe the featured subjects, uniforms, body builds, facial expression, arena context, camera framing, and lighting. "
        "Use only article-grounded details. If the article does not mention a face or jersey number, invent a plausible but non-famous anonymous athlete look that still fits the story. "
        "Do not mention brand names, copyrighted logos, on-image text, split panels, watermarks, fake newspaper layouts, animals, cats, statues, sculptures, mascots, plush toys, or figurines. "
        f"Include the uniqueness token '{facts['article_fingerprint']}' naturally near the end so similar articles do not collapse into the same composition."
    )
    user_query = (
        f"Headline: {facts['headline_context']}\n"
        f"Teams: {facts['teams']}\n"
        f"Possible players or subjects: {', '.join(facts['players']) if facts['players'] else 'anonymous NBA athletes'}\n"
        f"Uniform direction: {facts['uniform_notes']}\n"
        f"Color direction: {facts['color_notes']}\n"
        f"Primary action: {facts['action']}\n"
        f"Emotional tone: {facts['mood']}\n"
        f"Article snippet: {facts['content_context']}\n"
        "Write the final image prompt now."
    )
    prompt = llm.generate_response(user_query, system_prompt=system_prompt)
    cleaned_prompt = clean_generated_prompt(prompt or "")
    if not cleaned_prompt or "error" in cleaned_prompt.lower() or len(cleaned_prompt) < 80:
        return fallback_prompt
    return cleaned_prompt


def request_openai_image(prompt):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    response = requests.post(
        OPENAI_IMAGE_ENDPOINT,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": DEFAULT_IMAGE_MODEL,
            "prompt": prompt,
            "size": "1536x1024",
        },
        timeout=120,
    )
    response.raise_for_status()
    payload = response.json()
    image_b64 = payload["data"][0]["b64_json"]
    return Image.open(BytesIO(base64.b64decode(image_b64))).convert("RGB")


def create_fallback_canvas(title, prompt, news_id=None):
    seed_source = f"{news_id}|{title}|{prompt}".encode("utf-8")
    digest = hashlib.sha256(seed_source).digest()
    base_color = (50 + digest[0] % 120, 40 + digest[1] % 120, 60 + digest[2] % 120)
    accent_color = (110 + digest[3] % 120, 90 + digest[4] % 120, 80 + digest[5] % 120)

    img = Image.new("RGB", (OUTPUT_WIDTH, OUTPUT_HEIGHT), color=base_color)
    draw = ImageDraw.Draw(img)

    for idx in range(6):
        x0 = (digest[idx] * 3) % OUTPUT_WIDTH
        y0 = (digest[idx + 6] * 2) % OUTPUT_HEIGHT
        x1 = min(OUTPUT_WIDTH, x0 + 120 + digest[idx + 12] % 180)
        y1 = min(OUTPUT_HEIGHT, y0 + 80 + digest[idx + 18] % 140)
        alpha_like = 40 + digest[idx + 24] % 70
        shape_color = tuple(min(255, channel + alpha_like) for channel in accent_color)
        draw.ellipse((x0, y0, x1, y1), fill=shape_color)

    try:
        title_font = ImageFont.truetype("arial.ttf", 28)
        meta_font = ImageFont.truetype("arial.ttf", 16)
    except Exception:
        title_font = ImageFont.load_default()
        meta_font = ImageFont.load_default()

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle((20, OUTPUT_HEIGHT - 150, OUTPUT_WIDTH - 20, OUTPUT_HEIGHT - 20), radius=20, fill=(10, 10, 10, 170))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    draw.text((36, OUTPUT_HEIGHT - 138), title[:82], fill=(255, 255, 255), font=title_font)
    draw.text((36, OUTPUT_HEIGHT - 88), prompt[:150], fill=(235, 235, 235), font=meta_font)
    draw.text((36, 24), f"Generated fallback | {PROMPT_VERSION}", fill=(255, 255, 255), font=meta_font)
    return img


def create_news_image(output_path, text="News", news_id=None, prompt=None):
    prompt = clean_generated_prompt(prompt or build_fallback_prompt(text, text, news_id=news_id))

    try:
        img = request_openai_image(prompt)
        img = ImageOps.fit(img, (OUTPUT_WIDTH, OUTPUT_HEIGHT), method=Image.Resampling.LANCZOS)
        print(f"Generated image with model {DEFAULT_IMAGE_MODEL} for NewsID {news_id}")
    except Exception as e:
        print(f"Image generation failed for NewsID {news_id}: {e}. Using deterministic fallback art.")
        img = create_fallback_canvas(text, prompt, news_id=news_id)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Saved image to {output_path}")


def prompt_needs_refresh(prompt):
    if not prompt:
        return True
    cleaned = clean_generated_prompt(prompt)
    legacy_prefixes = (
        "NBA basketball action,",
        "basketball action,",
    )
    return len(cleaned) < 80 or cleaned.startswith(legacy_prefixes) or PROMPT_VERSION not in cleaned


def update_news_with_images(limit=10, force_refresh=False):
    """Process the image queue for news items."""
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            f'''
            SELECT "NewsID", "Title", "Content", "ImagePrompt", "ImageStatus"
            FROM "{DB_SCHEMA}"."News"
            WHERE "ImageStatus" IN ('pending', 'failed', 'completed') OR "ImageStatus" IS NULL
            ORDER BY "Date" DESC
            LIMIT %s
            ''',
            (limit,),
        )
        candidate_rows = cur.fetchall()

        for news_id, title, content, current_prompt, image_status in candidate_rows:
            if force_refresh or image_status in (None, "pending", "failed") or prompt_needs_refresh(current_prompt):
                print(f"Preparing fresh prompt for NewsID {news_id}...")
                generated_prompt = preprocess_image_prompt(title, content or "", news_id=news_id)
                versioned_prompt = f"{generated_prompt} {PROMPT_VERSION}".strip()
                cur.execute(
                    f'''
                    UPDATE "{DB_SCHEMA}"."News"
                    SET "ImagePrompt" = %s, "ImageStatus" = 'pending'
                    WHERE "NewsID" = %s
                    ''',
                    (versioned_prompt, news_id),
                )
        conn.commit()

        cur.execute(
            f'''
            SELECT "NewsID", "Title", "ImagePrompt"
            FROM "{DB_SCHEMA}"."News"
            WHERE "ImageStatus" = 'pending'
            ORDER BY "Date" DESC
            LIMIT %s
            ''',
            (limit,),
        )
        news_items = cur.fetchall()

        if not news_items:
            print("No pending news images to generate.")
            return

        for news_id, title, prompt in news_items:
            cur.execute(
                f'UPDATE "{DB_SCHEMA}"."News" SET "ImageStatus" = \'processing\' WHERE "NewsID" = %s',
                (news_id,),
            )
            conn.commit()

            image_filename = f"news_{news_id}.png"
            relative_path = os.path.join("assets", "news_images", image_filename)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            absolute_path = os.path.join(base_dir, relative_path)

            try:
                create_news_image(absolute_path, title, news_id, prompt)
                cur.execute(
                    f'''
                    UPDATE "{DB_SCHEMA}"."News"
                    SET "ImageURL" = %s, "ImageStatus" = 'completed'
                    WHERE "NewsID" = %s
                    ''',
                    (relative_path, news_id),
                )
                print(f"Successfully processed NewsID {news_id}")
            except Exception as e:
                print(f"Failed to process NewsID {news_id}: {e}")
                cur.execute(
                    f'UPDATE "{DB_SCHEMA}"."News" SET "ImageStatus" = \'failed\' WHERE "NewsID" = %s',
                    (news_id,),
                )

            conn.commit()

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error in image queue: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate or refresh NBA news images.")
    parser.add_argument("--limit", type=int, default=10, help="Number of news rows to process.")
    parser.add_argument("--force-refresh", action="store_true", help="Regenerate prompts and images even for completed or legacy items.")
    args = parser.parse_args()
    update_news_with_images(limit=args.limit, force_refresh=args.force_refresh)
