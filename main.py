from rss_fetcher import fetch_articles
from db import insert_articles, ai_summarize

def main():
    print("Starting RSS ingestion...\n")

    articles = fetch_articles()

    print("\nTotal articles collected:", len(articles))

    print("Inserting into database...")
    insert_articles(articles)

    print("Summarizing By SINS")
    ai_summarize()


if __name__ == "__main__":
    main()
