import os

import pandas as pd
import streamlit as st

from db_config import DB_SCHEMA, get_connection
from generate_news_images import update_news_with_images


def app():
    st.title("News Image Queue Manager")

    if st.button("Refresh Queue Status"):
        st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Generate 10 Pending Images"):
            update_news_with_images(limit=10)
            st.success("Triggered generation for the next 10 pending news images.")
    with c2:
        if st.button("Refresh 10 Recent Legacy Images"):
            update_news_with_images(limit=10, force_refresh=True)
            st.success("Triggered a forced refresh for 10 recent news images.")

    try:
        conn = get_connection()

        stats_query = f'''
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN "ImageStatus" = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN "ImageStatus" = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN "ImageStatus" = 'processing' THEN 1 END) as processing,
                COUNT(CASE WHEN "ImageStatus" = 'failed' THEN 1 END) as failed,
                COUNT(CASE WHEN "ImageStatus" IS NULL THEN 1 END) as untracked
            FROM "{DB_SCHEMA}"."News"
        '''
        stats_df = pd.read_sql_query(stats_query, conn)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total News", stats_df["total"][0])
        m2.metric("Images Ready", stats_df["completed"][0])
        m3.metric("Pending", stats_df["pending"][0])
        m4.metric("Failed", stats_df["failed"][0])

        st.subheader("Recent News Image Status")
        list_query = f'''
            SELECT
                "NewsID", "Date", "Title", "ImageStatus", "ImagePrompt", "ImageURL"
            FROM "{DB_SCHEMA}"."News"
            ORDER BY "Date" DESC
            LIMIT 50
        '''
        list_df = pd.read_sql_query(list_query, conn)

        def style_status(val):
            color = "gray"
            if val == "completed":
                color = "green"
            elif val == "pending":
                color = "orange"
            elif val == "processing":
                color = "blue"
            elif val == "failed":
                color = "red"
            return f"color: {color}"

        st.dataframe(
            list_df.style.map(style_status, subset=["ImageStatus"]),
            use_container_width=True,
            column_config={
                "ImageURL": st.column_config.LinkColumn("Path"),
                "ImagePrompt": st.column_config.TextColumn("AI Prompt", width="large"),
            },
        )

        st.subheader("Latest Generated Images")
        cur = conn.cursor()
        cur.execute(
            f'SELECT "Title", "ImageURL" FROM "{DB_SCHEMA}"."News" WHERE "ImageURL" IS NOT NULL ORDER BY "Date" DESC LIMIT 4'
        )
        previews = cur.fetchall()

        if previews:
            pcols = st.columns(4)
            for i, (title, url) in enumerate(previews):
                with pcols[i]:
                    if os.path.exists(url):
                        st.image(url, caption=title[:30] + "...")
                    else:
                        st.warning("File missing")

        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Database Error: {e}")


if __name__ == "__main__":
    app()
