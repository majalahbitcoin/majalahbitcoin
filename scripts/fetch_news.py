
import feedparser
import json
import os
import datetime
import requests
import google.generativeai as genai

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-pro")
else:
    print("GEMINI_API_KEY not set. Translation will be skipped.")
    model = None

RSS_FEEDS = [
    "https://bitcoinmagazine.com/feed",
    # Add more free Bitcoin RSS feeds here
]

OUTPUT_DIR = "./data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "news.json")

def translate_text(text, target_language="Malay"):
    if not model:
        return text # Return original text if no API key
    try:
        prompt = f"Translate the following English text to {target_language}. Only provide the translated text, without any additional commentary or conversational filler:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error translating text: {e}")
        return text # Return original text on error

def fetch_and_process_news():
    all_articles = []
    existing_article_ids = set()

    # Load existing news to avoid duplicates and preserve older articles
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            try:
                existing_articles = json.load(f)
                all_articles.extend(existing_articles)
                existing_article_ids = {article["id"] for article in existing_articles}
            except json.JSONDecodeError:
                print("Existing news.json is empty or malformed. Starting fresh.")

    for feed_url in RSS_FEEDS:
        print(f"Fetching news from: {feed_url}")
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                article_id = entry.id if hasattr(entry, 'id') else entry.link # Use entry.id or link as a unique identifier
                if article_id in existing_article_ids:
                    continue # Skip if article already exists

                title = entry.title
                summary = entry.summary if hasattr(entry, 'summary') else entry.title
                link = entry.link
                published = entry.published if hasattr(entry, 'published') else datetime.datetime.now(datetime.timezone.utc).isoformat()
                author = entry.author if hasattr(entry, 'author') else "Unknown"

                # Attempt to get a better image (if available in media_content or description)
                image_url = None
                if hasattr(entry, 'media_content') and entry.media_content:
                    for media in entry.media_content:
                        if media.get('type', '').startswith('image/') and media.get('url'):
                            image_url = media['url']
                            break
                if not image_url and hasattr(entry, 'description'):
                    # Basic regex to find an image in description, if no media_content
                    import re
                    match = re.search(r'<img[^>]+src=["\"]([^"\"]+)["\"]', entry.description)
                    if match: 
                        image_url = match.group(1)
                
                # Fallback image if none found
                if not image_url:
                    image_url = "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?auto=format&fit=crop&w=800&q=80" # Default Bitcoin image

                # Fetch full content if possible (simple approach, might need more sophisticated parsing)
                full_content = ""
                try:
                    response = requests.get(link, timeout=10)
                    response.raise_for_status()
                    # This is a very basic way to get content, for a real site, you'd use a library like BeautifulSoup
                    # For now, we'll just use the summary as content if full content is hard to extract
                    full_content = summary # Default to summary
                except requests.exceptions.RequestException as e:
                    print(f"Could not fetch full content for {link}: {e}")
                    full_content = summary

                # Translate title, summary, and content
                translated_title = translate_text(title)
                translated_summary = translate_text(summary)
                translated_content = translate_text(full_content) # Translate the fetched content or summary

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
            print(f"Error fetching or processing feed {feed_url}: {e}")

    # Sort articles by date, newest first
    all_articles.sort(key=lambda x: x.get("date", ""), reverse=True)

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    print(f"Successfully fetched and saved {len(all_articles)} articles to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_and_process_news()
