
import feedparser
import json
import os
import datetime
import requests
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, InvalidArgument

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
        print("Warning: Gemini API not configured. Skipping translation.")
        return text # Return original text if no API key
    if not text or text.strip() == "":
        return "" # Return empty string if there's nothing to translate
    try:
        prompt = f"Translate the following English text to {target_language}. Only provide the translated text, without any additional commentary or conversational filler:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except ResourceExhausted:
        print(f"Error: Gemini API rate limit exceeded for text: {text[:50]}...")
        return text # Return original text on rate limit error
    except InvalidArgument as e:
        print(f"Error: Invalid argument for Gemini API (e.g., unsafe content) for text: {text[:50]}... Error: {e}")
        return text # Return original text on invalid argument error
    except Exception as e:
        print(f"An unexpected error occurred during translation for text: {text[:50]}... Error: {e}")
        return text # Return original text on any other error

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
            except Exception as e:
                print(f"Error loading existing news.json: {e}. Starting fresh.")

    for feed_url in RSS_FEEDS:
        print(f"Fetching news from: {feed_url}")
        try:
            feed = feedparser.parse(feed_url)
            if feed.bozo:
                print(f"Warning: Malformed feed from {feed_url}: {feed.bozo_exception}")

            for entry in feed.entries:
                article_id = entry.id if hasattr(entry, 'id') else entry.link # Use entry.id or link as a unique identifier
                if not article_id:
                    print(f"Skipping entry due to missing ID/link: {entry.title if hasattr(entry, 'title') else 'Unknown Title'}")
                    continue

                if article_id in existing_article_ids:
                    continue # Skip if article already exists

                title = getattr(entry, 'title', 'No Title')
                summary = getattr(entry, 'summary', title) # Fallback to title if no summary
                link = getattr(entry, 'link', '#')
                published_date = getattr(entry, 'published_parsed', None)
                if published_date:
                    published = datetime.datetime(*published_date[:6], tzinfo=datetime.timezone.utc).isoformat()
                else:
                    published = datetime.datetime.now(datetime.timezone.utc).isoformat()
                author = getattr(entry, 'author', "Unknown")

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
                full_content = summary # Default to summary
                if link and link != '#': # Only try to fetch if a valid link exists
                    try:
                        response = requests.get(link, timeout=10)
                        response.raise_for_status()
                        # In a real scenario, you'd parse response.text with BeautifulSoup to extract main content
                        # For this static site, we'll stick to summary for content for simplicity and to avoid complex parsing
                        # If a more robust content extraction is needed, a dedicated parsing library would be required.
                        # For now, we'll assume summary is sufficient or improve it with a simple heuristic.
                        # Example: if summary is very short, try to get more from the page, but this is complex.
                        # Sticking to summary for content to keep it simple and free.
                        pass # No change to full_content, it remains summary
                    except requests.exceptions.RequestException as e:
                        print(f"Could not fetch full content for {link}: {e}")

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
    try:
        fetch_and_process_news()
    except Exception as e:
        print(f"An unhandled error occurred during news fetching: {e}")
        exit(1) # Exit with a non-zero code to indicate failure
