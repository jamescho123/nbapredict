import psycopg2
from PIL import Image, ImageDraw, ImageFont
import os
import random
import requests
from io import BytesIO
from db_config import get_connection, DB_SCHEMA
from app_pages.llm_interface import OllamaChat

def preprocess_image_prompt(title, content):
    """Use LLM to generate a descriptive image prompt based on news content"""
    llm = OllamaChat()
    if not llm.is_available:
        return f"NBA basketball action, {title}"
    
    system_prompt = """You are an expert at writing image generation prompts for sports news.
    Your goal is to create a concise, visually rich prompt (20-30 words) for a high-quality, photo-realistic NBA photograph in a consistent Nano Banana style.
    Always:
    - Describe player body shape and build (e.g. tall lean guard, strong muscular center).
    - Specify uniform details: home or away, approximate team colors from the news, jersey numbers but no real logos or text.
    - Add facial expression and emotion (intense focus, celebration, frustration, etc.).
    - Mention camera angle and framing (courtside close-up, wide arena shot, dynamic low angle, overhead, etc.).
    - Include relevant context: home arena or away court, crowd energy, scoreboard or clock tension if it fits the story.
    - Use cinematic, dramatic sports lighting and vivid but realistic colors.
    Keep everything consistent with the headline and content, avoid specific copyrighted logos or real player likenesses.
    Return ONLY the prompt string, no explanations."""
    
    user_query = f"Create a realistic NBA photo prompt for this news: {title}. Content snippet: {content[:200]}"
    
    prompt = llm.generate_response(user_query, system_prompt=system_prompt)
    if not prompt or "Error" in prompt:
        return f"NBA basketball action, {title}"
    
    return prompt.strip()

def create_news_image(output_path, text="News", news_id=None, prompt=None):
    width, height = 800, 450
    
    search_query = prompt if prompt else f"basketball,nba,{text}"
    # Clean query for URL
    clean_query = ",".join([s.strip() for s in search_query.split() if len(s) > 2][:3])
    
    # Try to fetch a real image related to basketball
    try:
        # Use loremflickr with basketball keyword and a stronger unique seed per news item
        unique_seed = f"{news_id}_{random.randint(0, 1_000_000)}" if news_id is not None else random.randint(0, 1_000_000)
        image_url = f"https://loremflickr.com/{width}/{height}/{clean_query}?lock={news_id}&random={unique_seed}"
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert('RGB')
        print(f"Fetched image from {image_url}")
    except Exception as e:
        print(f"Failed to fetch image: {e}. Falling back to placeholder.")
        color = (random.randint(0, 100), random.randint(0, 50), random.randint(50, 150)) # dark blue-ish
        img = Image.new('RGB', (width, height), color=color)

    d = ImageDraw.Draw(img)
    
    # Try to use a default font
    try:
        font = ImageFont.truetype("arial.ttf", 40)
        small_font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Add a semi-transparent overlay at the bottom for text readability
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d_overlay = ImageDraw.Draw(overlay)
    d_overlay.rectangle([(0, height - 120), (width, height)], fill=(0, 0, 0, 150))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    d = ImageDraw.Draw(img)

    # Draw title text (bottom left)
    d.text((20, height - 100), text[:50] + "..." if len(text) > 50 else text, fill=(255, 255, 255), font=font)
    
    # Add a "Nano Banana Style" watermark (top left)
    d.text((20, 20), "Nano Banana Style", fill=(255, 255, 255, 180), font=small_font)

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Saved image to {output_path}")

def update_news_with_images(limit=10):
    """Process the image queue for news items"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # 1. First, preprocess prompts for pending items that don't have one
        cur.execute(f'''
            SELECT "NewsID", "Title", "Content" 
            FROM "{DB_SCHEMA}"."News" 
            WHERE ("ImageStatus" = 'pending' OR "ImageStatus" IS NULL) 
            AND "ImagePrompt" IS NULL
            ORDER BY "Date" DESC 
            LIMIT %s
        ''', (limit,))
        
        to_preprocess = cur.fetchall()
        for news_id, title, content in to_preprocess:
            print(f"Preprocessing prompt for NewsID {news_id}...")
            prompt = preprocess_image_prompt(title, content)
            cur.execute(f'UPDATE "{DB_SCHEMA}"."News" SET "ImagePrompt" = %s, "ImageStatus" = \'pending\' WHERE "NewsID" = %s', (prompt, news_id))
        conn.commit()

        # 2. Process the queue
        cur.execute(f'''
            SELECT "NewsID", "Title", "ImagePrompt" 
            FROM "{DB_SCHEMA}"."News" 
            WHERE "ImageStatus" = 'pending' 
            ORDER BY "Date" DESC 
            LIMIT %s
        ''', (limit,))
        
        news_items = cur.fetchall()
        
        if not news_items:
            print("No pending news images to generate.")
            return

        for news_id, title, prompt in news_items:
            # Mark as processing
            cur.execute(f'UPDATE "{DB_SCHEMA}"."News" SET "ImageStatus" = \'processing\' WHERE "NewsID" = %s', (news_id,))
            conn.commit()
            
            # Generate filenames
            image_filename = f"news_{news_id}.png"
            
            # Define paths
            relative_path = os.path.join("assets", "news_images", image_filename)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            absolute_path = os.path.join(base_dir, relative_path)
            
            try:
                # Create image
                create_news_image(absolute_path, title, news_id, prompt)
                
                # Update DB with relative path and status
                cur.execute(f'''
                    UPDATE "{DB_SCHEMA}"."News" 
                    SET "ImageURL" = %s, "ImageStatus" = 'completed' 
                    WHERE "NewsID" = %s
                ''', (relative_path, news_id))
                print(f"Successfully processed NewsID {news_id}")
            except Exception as e:
                print(f"Failed to process NewsID {news_id}: {e}")
                cur.execute(f'UPDATE "{DB_SCHEMA}"."News" SET "ImageStatus" = \'failed\' WHERE "NewsID" = %s', (news_id,))
            
            conn.commit()
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error in image queue: {e}")

if __name__ == "__main__":
    update_news_with_images()
