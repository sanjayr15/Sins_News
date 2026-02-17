import feedparser
from datetime import datetime
from config import RSS_FEEDS
from bs4 import BeautifulSoup
import hashlib
from newspaper import Article
import trafilatura

def fetch_full_article(url):
    # article = Article(url)
    # article.download()
    # article.parse()
    
    # return article.text

    downloaded = trafilatura.fetch_url(url)
    text = trafilatura.extract(downloaded)

    return text




def generate_hash(title, summary):
    combined = (title or "") + (summary or "")
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def clean_html(raw_html):
    if not raw_html:
        return None
    
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(strip=True)

def extract_image(entry):
    # Case 1: media_content
    if "media_content" in entry:
        return entry.media_content[0]["url"]

    # Case 2: media_thumbnail
    if "media_thumbnail" in entry:
        return entry.media_thumbnail[0]["url"]

    # Case 3: enclosure
    if "links" in entry:
        for link in entry.links:
            if link.get("type", "").startswith("image"):
                return link.get("href")

    # Case 4: extract from summary HTML
    if "summary" in entry:
        soup = BeautifulSoup(entry.summary, "html.parser")
        img = soup.find("img")
        if img:
            return img.get("src")

    return None


def fetch_articles():
    all_articles = []

    for source, url in RSS_FEEDS.items():
        print(f"\nFetching from {source}...")

        feed = feedparser.parse(url)

        if feed.bozo:
            print(f"Error parsing feed: {url}")
            continue

        for entry in feed.entries:
            article = {
                "source": source,
                "title": entry.get("title"),
                "link": entry.get("link"),
                "published": entry.get("published"),
                "summary": clean_html(entry.get("summary")),
                "image_url": extract_image(entry),
                "content_hash" : generate_hash(entry.get("title"),clean_html(entry.get("summary"))),
                "fetched_at": datetime.utcnow()
            }
            all_articles.append(article)

        print(f"Collected {len(feed.entries)} articles from {source}")

    return all_articles
