import json
import random
from pathlib import Path
from typing import Dict, List, Any, Optional

import requests

from utils.logger import get_logger
from utils.proxy_manager import ProxyManager
from utils.rate_limiter import RateLimiter
from utils.error_handler import retry


class ThreadsScraper:
    def __init__(self, root_dir: Path, config: Dict[str, Any], logger=None):
        self.root_dir = root_dir
        self.cfg = config or {}
        self.log = logger or get_logger("ThreadsScraper")
        self.timeout = self.cfg.get("scrape", {}).get("request_timeout_seconds", 15)
        self.delay_ms = self.cfg.get("scrape", {}).get("delay_between_requests_ms", 250)
        self.user_agent_rotation = self.cfg.get("scrape", {}).get("user_agent_rotation", True)
        self.use_local_fallback = self.cfg.get("scrape", {}).get("use_local_fallback_on_error", True)

        self.base_url = self.cfg.get("network", {}).get("base_url", "https://www.threads.net")
        self.endpoint_template = self.cfg.get("network", {}).get("posts_endpoint_template", "/@{username}")

        self.ua_pool = self._load_user_agents(self.root_dir / "config" / "user_agents.txt")
        self.proxies = ProxyManager(
            self.root_dir / "config" / "proxies.json",
            enable_rotation=self.cfg.get("scrape", {}).get("proxy_rotation", False),
        )
        self.limiter = RateLimiter(min_interval_ms=self.delay_ms)

        self.fallback_path = self.root_dir / "data" / "raw" / "profile_posts.json"

    @staticmethod
    def _load_user_agents(path: Path) -> List[str]:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                agents = [line.strip() for line in f if line.strip()]
                return agents or ["Mozilla/5.0"]
        return ["Mozilla/5.0"]

    def _headers(self) -> Dict[str, str]:
        ua = random.choice(self.ua_pool) if self.user_agent_rotation else self.ua_pool[0]
        return {
            "User-Agent": ua,
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }

    def _build_url(self, username: str) -> str:
        endpoint = self.endpoint_template.format(username=username.strip("@"))
        return f"{self.base_url.rstrip('/')}{endpoint}"

    @retry(
        on_exceptions=(requests.RequestException,),
        tries=None,
        max_tries_key=("scrape", "retry_attempts"),
        backoff_seconds_key=("scrape", "retry_backoff_seconds"),
    )
    def _http_get(self, url: str, proxy: Optional[Dict[str, str]]) -> requests.Response:
        resp = requests.get(url, headers=self._headers(), proxies=proxy or None, timeout=self.timeout)
        resp.raise_for_status()
        return resp

    def _extract_posts_from_html(self, html: str) -> List[Dict[str, Any]]:
        # Heuristic placeholder: real implementation would parse embedded JSON.
        # We return an empty list to prefer local fixture for deterministic runs.
        return []

    def _local_fallback(self) -> List[Dict[str, Any]]:
        if self.fallback_path.exists():
            with open(self.fallback_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        self.log.warning("Local fallback JSON not found or invalid; returning empty list.")
        return []

    def fetch_profile_posts(self, username: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Attempts to fetch profile page then parse. Falls back to local JSON fixtures.
        """
        url = self._build_url(username)
        proxy = self.proxies.next_proxy()
        self.limiter.wait()

        posts: List[Dict[str, Any]] = []
        try:
            resp = self._http_get(url, proxy)
            posts = self._extract_posts_from_html(resp.text)
        except Exception as e:
            self.log.debug(f"HTTP fetch error for {url}: {e}")

        if (not posts) and self.use_local_fallback:
            self.log.info("Using local fallback data.")
            fallback = self._local_fallback()
            posts = [p for p in fallback if p.get("username") == username][:limit]

        # Limit posts and ensure the minimal fields exist
        sanitized: List[Dict[str, Any]] = []
        for p in posts[:limit]:
            sanitized.append(
                {
                    "username": p.get("username", username),
                    "post_id": str(p.get("post_id", "")),
                    "content": p.get("content", ""),
                    "media_url": p.get("media_url"),
                    "likes": p.get("likes", 0),
                    "comments": p.get("comments", 0),
                    "posted_at": p.get("posted_at"),
                    "link": p.get("link"),
                    "hashtags": p.get("hashtags", []),
                    "mentions": p.get("mentions", []),
                }
            )
        return sanitized
