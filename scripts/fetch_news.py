
import feedparser
import json
import os
import datetime
import requests
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, InvalidArgument, NotFound

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Using gemini-1.5-flash as it's more likely to be available and faster for translation
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    print("GEMINI_API_KEY not set. Translation will be skipped.")
    model = None

RSS_FEEDS = [
    "https://bitcoinmagazine.com/feed",
]

OUTPUT_DIR = "./data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "news.json")

def translate_text(text, target_language="Malay"):
    if not model:
        return text
    if not text or text.strip() == "":
        return ""
    try:
        prompt = f"Translate the following English text to {target_language}. Only provide the translated text, without any additional commentary or conversational filler:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except (ResourceExhausted, InvalidArgument, NotFound, Exception) as e:
        print(f"Error translating text: {e}")
        return text

def fetch_and_process_news():
    all_articles = []
    existing_article_ids = set()

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            try:
                existing_articles = json.load(f)
                all_articles.extend(existing_articles)
                existing_article_ids = {article["id"] for article in existing_articles}
            except Exception as e:
                print(f"Error loading existing news: {e}")

    for feed_url in RSS_FEEDS:
        print(f"Fetching news from: {feed_url}")
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                article_id = entry.id if hasattr(entry, 'id') else entry.link
                if not article_id or article_id in existing_article_ids:
                    continue

                title = getattr(entry, 'title', 'No Title')
                summary = getattr(entry, 'summary', title)
                link = getattr(entry, 'link', '#')
                
                published_date = getattr(entry, 'published_parsed', None)
                if published_date:
                    published = datetime.datetime(*published_date[:6], tzinfo=datetime.timezone.utc).isoformat()
                else:
                    published = datetime.datetime.now(datetime.timezone.utc).isoformat()
                
                author = getattr(entry, 'author', "Unknown")

                image_url = None
                if hasattr(entry, 'media_content') and entry.media_content:
                    for media in entry.media_content:
                        if media.get('type', '').startswith('image/') and media.get('url'):
                            image_url = media['url']
                            break
                if not image_url and hasattr(entry, 'description'):
                    import re
                    match = re.search(r'<img[^>]+src=["\"]([^"\"]+)["\"]', entry.description)
                    if match: 
                        image_url = match.group(1)
                
                if not image_url:
                    image_url = "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?auto=format&fit=crop&w=800&q=80"

                # Translate
                translated_title = translate_text(title)
                translated_summary = translate_text(summary)
                translated_content = translate_text(summary) # Use summary as content for now

                article_data = {
                    "id": article_id,
                    "title": translated_title,
                    "summary": translated_summary,
                    "content": translated_content,
                    "date": published,
                    "author": author,
                    "image": image_url,
                    "source_url": link
                }
                all_articles.append(article_data)
                existing_article_ids.add(article_id)

        except Exception as e:
            print(f"Error processing feed {feed_url}: {e}")

    all_articles.sort(key=lambda x: x.get("date", ""), reverse=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    print(f"Successfully fetched and saved {len(all_articles)} articles to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_and_process_news()
