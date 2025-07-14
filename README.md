Reddit Persona Builder

This project extracts Reddit posts and comments from a given user's profile and uses Google's Gemini Pro API to generate a structured user persona based on their behavior, values, motivations, and personality traits.

Tech:

- Python
- PRAW (Python Reddit API Wrapper)
- Gemini Pro (Google Generative AI)
- dotenv (`.env` for environment management)

Setup:

1. Clone the Repository
```bash
git clone https://github.com/your-username/reddit-persona-builder.git
cd reddit-persona-builder
```

2. Make a copy of .env.example and rename it to .env. Fill in your API keys:
  REDDIT_CLIENT_ID=your_reddit_client_id
  REDDIT_CLIENT_SECRET=your_reddit_client_secret
  GEMINI_API_KEY=your_google_gemini_api_key

3. Install Dependencies
```
pip install -r requirements.txt
```

4. Run the script
```
python reddit_persona_script.py <reddit_profile_url> [num_posts] [num_comments]
```
Example:
```
python reddit_persona_script.py https://www.reddit.com/user/kojied/ 8 15
```
