from pathlib import Path
import yaml

from src.scraper import ThreadsScraper


def _test_config(root: Path):
    with open(root / "config" / "settings.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    # Speed up tests
    cfg["scrape"]["retry_attempts"] = 1
    cfg["scrape"]["use_local_fallback_on_error"] = True
    cfg["scrape"]["proxy_rotation"] = False
    cfg["scrape"]["user_agent_rotation"] = False
    return cfg


def test_fetch_uses_local_fixture(tmp_path):
    root = Path(__file__).resolve().parents[1]
    cfg = _test_config(root)
    scraper = ThreadsScraper(root, cfg)
    posts = scraper.fetch_profile_posts("example_user_1", limit=5)
    assert isinstance(posts, list)
    assert len(posts) > 0
    assert posts[0]["username"] == "example_user_1"
    assert "post_id" in posts[0]
