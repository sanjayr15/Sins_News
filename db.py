import psycopg2
from sins_ai import generate_summary_and_category
import pandas as pd
import os
from rss_fetcher import fetch_full_article
import requests

SUPABASE_URL = "https://ykygmtvpzlyenkzazils.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlreWdtdHZwemx5ZW5remF6aWxzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzExMjM5NDEsImV4cCI6MjA4NjY5OTk0MX0.C6p6TRHjT_1T7RCCb_9OEic35fYMoUMYNS1BSMcjLxc"

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)



def get_full_content():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    		SELECT id, source_title, source_link
		    FROM articles
		    WHERE source_full_content IS NULL
    """)

    rows = cur.fetchall()

    for row in rows:
        article_id, title, link = row
        full_content = fetch_full_article(link)
        
        if full_content is not None:
            cur.execute("""
                UPDATE articles
                set source_full_content = %s
                where id = %s 
            """,(full_content,article_id))
            conn.commit()
    cur.close()
    conn.close()




def insert_articles(articles):
    conn = get_connection()
    cur = conn.cursor()

    insert_query = """
        INSERT INTO articles 
        (source, source_title, source_link, source_published, source_summary, source_image_url, sins_hash_value, fetched_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
    """

    for article in articles:
        try:
            cur.execute(insert_query, (
                article["source"],
                article["title"],
                article["link"],
                article["published"],
                article["summary"],
                article["image_url"],
                article["content_hash"],
                article["fetched_at"]
            ))
        except Exception as e:
            print("Insert error:", e)

    conn.commit()
    cur.close()
    conn.close()

    print("Database insertion complete.")


#AI Summarize

def ai_summarize():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    		SELECT id, source_title, source_summary
		    FROM articles
		    WHERE sins_summary IS NULL
    """)

    rows = cur.fetchall()

    for row in rows:
        article_id, title, description = row

        title, summary, category, veridct, sin_meter = generate_summary_and_category(title, description)

        if summary:
            cur.execute("""
                UPDATE articles
                SET 
                    sins_title = %s,
                    sins_summary = %s,
                    sins_category = %s,
                    sins_verdict = %s,
                    sins_meter = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (title, summary, category, veridct, sin_meter, article_id))

            conn.commit()
            print(f"Processed article {article_id}")

    cur.close()
    conn.close()





# Data Retrival for UI
def get_ai_data():
    conn = get_connection()
    #cur = conn.cursor()

    query = """
    SELECT id, source, sins_title, sins_summary, sins_category, sins_verdict, sins_meter, source_image_url, source_link, source_full_content,cast(fetched_at as date) as fetched_at
    FROM articles
    where sins_summary is not null
    ORDER BY sins_meter DESC,source_published DESC
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df


def add_like(article_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO article_likes (article_id)
        VALUES (%s)
    """, (article_id,))

    conn.commit()
    cur.close()
    conn.close()

def get_like_count(article_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*) 
        FROM article_likes
        WHERE article_id = %s
    """, (article_id,))

    count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return count

def get_likes_from_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT article_id, COUNT(*) as Count
        FROM article_likes
        group by article_id
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    likes_dict = {row[0]: row[1] for row in rows}

    return likes_dict

def add_comment(article_id, comment):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO article_comments (article_id, comment)
        VALUES (%s, %s)
    """, (article_id, comment))

    conn.commit()
    cur.close()
    conn.close()

def get_comments(article_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT comment, created_at
        FROM article_comments
        WHERE article_id = %s
        ORDER BY created_at DESC
    """, (article_id,))

    comments = cur.fetchall()

    cur.close()
    conn.close()

    return comments

# def get_specific_data(id):
#     conn = get_connection()
#     #cur = conn.cursor()

#     query = f"""
#     SELECT source_title, sins_summary, sins_category, sins_verdict, sins_meter, source_image_url, source_link, fetched_at
#     FROM articles
#     where id = {id}
#     ORDER BY source_published DESC
#     """

#     df = pd.read_sql(query, conn)
#     conn.close()

#     return df





