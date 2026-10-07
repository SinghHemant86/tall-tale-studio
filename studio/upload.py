"""YouTube upload via the official Data API (free quota). Uses a stored refresh token.

Needs env: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN  (get the token once with
scripts/get_youtube_token.py on your laptop, then save all three as GitHub secrets).
"""
import os
from pathlib import Path

from .common import log


def upload(video: Path, thumb: Path | None, title: str, meta: dict, cfg: dict,
           publish_at: str | None = None) -> str | None:
    """Upload; with publish_at (RFC 3339 UTC) the video stays private and goes public at that time."""
    need = ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN")
    if not all(os.environ.get(k) for k in need):
        log("  youtube: credentials not set, skipping upload")
        return None

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = Credentials(
        None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"].strip(),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YT_CLIENT_ID"].strip(),
        client_secret=os.environ["YT_CLIENT_SECRET"].strip(),
        scopes=["https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.readonly"],
    )
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    ch = yt.channels().list(part="snippet", mine=True).execute().get("items", [])
    want = cfg["youtube"].get("channel_id")
    got = ch[0]["id"] if ch else None
    if want and got != want:
        raise RuntimeError(f"Connected to channel {got}, expected Tall-Tale ({want}). Refusing to upload. "
                           "Re-run scripts/get_youtube_token.ps1 and pick the Tall-Tale channel.")
    log(f"  youtube: uploading to channel '{ch[0]['snippet']['title'] if ch else 'unknown'}'")
    ycfg = cfg["youtube"]
    body = {
        "snippet": {
            "title": title[:100],
            "description": meta.get("description", "")[:4900],
            "tags": meta.get("tags", [])[:30],
            "categoryId": ycfg.get("category_id", "24"),
            "defaultLanguage": meta.get("text_language", "en"),
            "defaultAudioLanguage": meta.get("audio_language", "hi"),
        },
        "status": {
            "privacyStatus": ycfg.get("privacy", "private"),
            "selfDeclaredMadeForKids": ycfg.get("made_for_kids", False),
            "containsSyntheticMedia": True,  # AI-generated visuals/voices must be disclosed
        },
    }
    if publish_at:
        body["status"]["privacyStatus"] = "private"   # required for scheduled publishing
        body["status"]["publishAt"] = publish_at
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(video), chunksize=8 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            log(f"  youtube: {int(status.progress() * 100)}%")
    vid = resp["id"]
    if thumb and thumb.exists():
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb))).execute()
        except Exception as e:  # noqa: BLE001  (custom thumbnails need a verified channel)
            log(f"  youtube: thumbnail not set ({e!s:.100})")
    when = f", goes public {publish_at}" if publish_at else ""
    log(f"  youtube: uploaded https://youtu.be/{vid} ({body['status']['privacyStatus']}{when})")
    return vid
