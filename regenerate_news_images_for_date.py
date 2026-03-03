from datetime import date

from db_config import get_connection, DB_SCHEMA
from generate_news_images import update_news_with_images


def regenerate_images_for_date(target_date: date) -> None:
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Reset image fields for the target date so prompts are regenerated
        cur.execute(
            f'''
            UPDATE "{DB_SCHEMA}"."News"
            SET "ImageStatus" = 'pending',
                "ImagePrompt" = NULL,
                "ImageURL" = NULL
            WHERE "Date"::date = %s
            ''',
            (target_date,),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

    # Process all pending items (large limit to be safe)
    update_news_with_images(limit=500)


if __name__ == "__main__":
    regenerate_images_for_date(date(2026, 2, 6))
