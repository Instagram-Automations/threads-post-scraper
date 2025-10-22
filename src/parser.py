from typing import List, Dict, Any
from utils.logger import get_logger


class ThreadsParser:
    """
    Transforms raw post dicts into normalized records with consistent keys and types.
    """

    def __init__(self, logger=None):
        self.log = logger or get_logger("ThreadsParser")

    def parse_posts(self, raw_posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        parsed: List[Dict[str, Any]] = []
        for item in raw_posts:
            try:
                record = {
                    "username": str(item.get("username", "")).strip(),
                    "post_id": str(item.get("post_id", "")).strip(),
                    "content": (item.get("content") or "").strip(),
                    "media_url": item.get("media_url") or None,
                    "likes": int(item.get("likes", 0) or 0),
                    "comments": int(item.get("comments", 0) or 0),
                    "posted_at": str(item.get("posted_at") or ""),
                    "link": item.get("link") or "",
                    "hashtags": item.get("hashtags") or [],
                    "mentions": item.get("mentions") or [],
                }
                # Only keep records with essential identifiers
                if record["username"] and record["post_id"]:
                    parsed.append(record)
            except Exception as e:
                self.log.warning(f"Skipping invalid item due to parse error: {e}")
        return parsed
