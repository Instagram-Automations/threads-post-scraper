import pandas as pd
from typing import List, Dict, Any
from utils.logger import get_logger


class DataCleaner:
    """
    Converts parsed records into a DataFrame, normalizes columns, and deduplicates.
    """

    def __init__(self, logger=None):
        self.log = logger or get_logger("DataCleaner")

    def clean(self, records: List[Dict[str, Any]]) -> pd.DataFrame:
        if not records:
            return pd.DataFrame(
                columns=[
                    "username",
                    "post_id",
                    "content",
                    "media_url",
                    "likes",
                    "comments",
                    "posted_at",
                    "link",
                    "hashtags",
                    "mentions",
                ]
            )

        df = pd.DataFrame.from_records(records)

        # Ensure list-like fields are strings for CSV friendliness while keeping objects in memory
        df["hashtags"] = df["hashtags"].apply(lambda x: ",".join(x) if isinstance(x, list) else str(x or ""))
        df["mentions"] = df["mentions"].apply(lambda x: ",".join(x) if isinstance(x, list) else str(x or ""))

        # Trim content and links
        df["content"] = df["content"].astype(str).str.strip()
        df["link"] = df["link"].astype(str).str.strip()

        # Deduplicate by (username, post_id)
        before = len(df)
        df = df.drop_duplicates(subset=["username", "post_id"]).reset_index(drop=True)
        after = len(df)
        if after < before:
            self.log.info(f"Deduplicated {before - after} rows.")

        # Sort by posted_at if provided
        if "posted_at" in df.columns:
            df["posted_at"] = df["posted_at"].astype(str)
            df = df.sort_values(by=["username", "posted_at", "post_id"]).reset_index(drop=True)

        # Enforce dtypes
        for col in ["likes", "comments"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

        return df
