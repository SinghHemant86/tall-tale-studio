"""Schedule already-uploaded videos: python scripts/publish.py VIDEO_ID=2026-10-11T12:46:00Z [...]"""
import os
import sys

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"].strip(),
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=os.environ["YT_CLIENT_ID"].strip(),
                    client_secret=os.environ["YT_CLIENT_SECRET"].strip())
yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
for arg in sys.argv[1:]:
    vid, at = arg.split("=", 1)
    cur = yt.videos().list(part="status", id=vid).execute()["items"][0]["status"]
    print(vid, "now:", cur)
    status = {"privacyStatus": "private", "publishAt": at, "selfDeclaredMadeForKids": False,
              "embeddable": cur.get("embeddable", True), "license": cur.get("license", "youtube"),
              "publicStatsViewable": cur.get("publicStatsViewable", True)}
    res = yt.videos().update(part="status", body={"id": vid, "status": status}).execute()
    print(vid, "scheduled:", res["status"])
