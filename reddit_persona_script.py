import sys
import os
import praw
import prawcore
from urllib.parse import urlparse
from dotenv import load_dotenv
import google.generativeai as genai

# --- Load environment variables from .env file ---
load_dotenv()

# --- Reddit API Setup ---
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="persona-builder-script"
)

# --- Gemini API Setup ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-pro")

# --- Extract username from Reddit profile URL ---
def extract_username(url):
    parts = urlparse(url).path.strip("/").split("/")
    return parts[-1] if parts[0] == "user" else None

# --- Get posts and comments for a user ---
def get_user_data(username, post_limit=10, comment_limit=20):
    try:
        user = reddit.redditor(username)
        posts = [
            {"id": i+1, "title": sub.title, "body": sub.selftext}
            for i, sub in enumerate(user.submissions.new(limit=post_limit))
        ]
        comments = [
            {"id": i+1, "body": c.body}
            for i, c in enumerate(user.comments.new(limit=comment_limit))
        ]
        return posts, comments
    except prawcore.exceptions.NotFound:
        print(f"[!] User '{username}' not found.")
        return [], []
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        return [], []

# --- Format labeled blocks for input ---
def prepare_text(posts, comments, max_chars=30000):
    all_text = ""
    for post in posts:
        chunk = f"Post #{post['id']}: {post['title']}\n{post['body']}\n\n"
        if len(all_text + chunk) > max_chars:
            break
        all_text += chunk
    for comment in comments:
        chunk = f"Comment #{comment['id']}: {comment['body']}\n"
        if len(all_text + chunk) > max_chars:
            break
        all_text += chunk
    return all_text

# --- Generate persona using Gemini ---
def generate_persona_with_gemini(text):
    prompt = f"""
You are an expert in behavioral analysis. Based on the Reddit posts and comments below, generate a structured user persona.
Include: personality traits, behaviors, values, motivations, frustrations, and goals. Be concise but insightful.
For each insight (trait, behavior, motivation, etc), cite the Post # or Comment # that supports it.

Reddit Content:
{text}
"""

    response = model.generate_content(prompt)
    return response.text

# --- Save output to file ---
def save_persona(username, persona_text):
    with open(f"{username}.txt", "w", encoding="utf-8") as f:
        f.write(persona_text)

# --- Main Script ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <reddit_profile_url> [num_posts] [num_comments]")
        sys.exit(1)

    url = sys.argv[1]
    post_limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    comment_limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20

    username = extract_username(url)

    if not username:
        print("Invalid Reddit profile URL.")
        sys.exit(1)

    print(f"[+] Fetching data for: {username}")
    posts, comments = get_user_data(username, post_limit, comment_limit)

    if not posts and not comments:
        print("[!] No data found to generate a persona.")
        sys.exit(1)

    print("[+] Preparing text")
    full_text = prepare_text(posts, comments)

    print("[+] Generating persona using Gemini")
    persona = generate_persona_with_gemini(full_text)

    if len(persona.strip().split()) < 20:
        print("[!] Warning: Persona output seems too short.")

    print("[+] Saving persona to file")
    save_persona(username, persona)

    print(f"Persona saved as {username}.txt")
