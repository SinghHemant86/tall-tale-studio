"""Run ONCE on your laptop to get a YouTube refresh token for the cloud runs.

1. Google Cloud Console -> new project -> enable "YouTube Data API v3".
2. OAuth consent screen: External, add yourself as a test user, then PUBLISH the app
   (apps left in "Testing" get refresh tokens that expire after 7 days).
3. Credentials -> Create OAuth client ID -> "Desktop app" -> download JSON as client_secret.json
   next to this script.
4. pip install google-auth-oauthlib google-api-python-client  &&  python scripts/get_youtube_token.py
5. Sign in with the Google account that owns the channel. Copy the three printed values into
   GitHub -> repo Settings -> Secrets and variables -> Actions.
"""
import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

here = Path(__file__).parent
secret = here / "client_secret.json"
flow = InstalledAppFlow.from_client_secrets_file(
    str(secret), scopes=["https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.readonly"])
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
info = json.loads(secret.read_text())["installed"]

from googleapiclient.discovery import build
ch = build("youtube", "v3", credentials=creds).channels().list(part="snippet", mine=True).execute()
if ch.get("items"):
    c = ch["items"][0]
    print(f"\nConnected channel: {c['snippet']['title']}  (https://youtube.com/channel/{c['id']})")
    print("If this is NOT your horror channel, run the script again and pick the right channel.")
print("\nAdd these as GitHub Actions secrets:\n")
print(f"YT_CLIENT_ID      = {info['client_id']}")
print(f"YT_CLIENT_SECRET  = {info['client_secret']}")
print(f"YT_REFRESH_TOKEN  = {creds.refresh_token}")
print("\nThen delete client_secret.json from this folder (never commit it).")
