import sys
from pathlib import Path
import yaml

from utils.logger import get_logger
from utils.error_handler import catch_exceptions
from scraper import ThreadsScraper
from parser import ThreadsParser
from cleaner import DataCleaner
from exporter import DataExporter


@catch_exceptions()
def main():
    root = Path(__file__).resolve().parents[1]
    config_path = root / "config" / "settings.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    log = get_logger(
        name="threads-post-scraper",
        level=cfg.get("logging", {}).get("level", "INFO"),
        json_mode=cfg.get("logging", {}).get("json", False),
        log_file=(root / cfg.get("logging", {}).get("file", "output/run.log")).as_posix(),
    )

    out_dir = root / cfg.get("output", {}).get("dir", "output")
    out_dir.mkdir(parents=True, exist_ok=True)

    scraper = ThreadsScraper(root_dir=root, config=cfg, logger=log)
    parser = ThreadsParser(logger=log)
    cleaner = DataCleaner(logger=log)
    exporter = DataExporter(output_dir=out_dir, logger=log)

    profiles = cfg.get("scrape", {}).get("profiles", [])
    max_posts = cfg.get("scrape", {}).get("max_posts_per_profile", 50)

    all_raw = []
    for username in profiles:
        log.info(f"Fetching posts for @{username}")
        raw_posts = scraper.fetch_profile_posts(username=username, limit=max_posts)
        all_raw.extend(raw_posts)

    log.info(f"Parsing {len(all_raw)} raw posts")
    parsed = parser.parse_posts(all_raw)

    log.info("Cleaning and normalizing data")
    cleaned_df = cleaner.clean(parsed)

    log.info("Exporting results")
    if cfg.get("output", {}).get("export_json", True):
        exporter.export_json(cleaned_df, filename="posts.json")
    if cfg.get("output", {}).get("export_csv", True):
        exporter.export_csv(cleaned_df, filename="posts.csv")
    if cfg.get("output", {}).get("export_summary", True):
        exporter.export_summary(cleaned_df, filename="summary_report.txt")

    log.info(f"Done. Rows exported: {len(cleaned_df)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
