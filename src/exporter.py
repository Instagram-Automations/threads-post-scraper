import json
from pathlib import Path
import pandas as pd
from utils.logger import get_logger


class DataExporter:
    def __init__(self, output_dir: Path, logger=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log = logger or get_logger("DataExporter")

    def export_json(self, df: pd.DataFrame, filename: str = "posts.json") -> Path:
        path = self.output_dir / filename
        records = df.to_dict(orient="records")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        self.log.info(f"Wrote JSON: {path}")
        return path

    def export_csv(self, df: pd.DataFrame, filename: str = "posts.csv") -> Path:
        path = self.output_dir / filename
        df.to_csv(path, index=False, encoding="utf-8")
        self.log.info(f"Wrote CSV: {path}")
        return path

    def export_summary(self, df: pd.DataFrame, filename: str = "summary_report.txt") -> Path:
        path = self.output_dir / filename
        lines = []
        lines.append(f"Total posts: {len(df)}")
        if not df.empty:
            lines.append(f"Profiles covered: {df['username'].nunique()}")
            top_like = df.sort_values("likes", ascending=False).head(1)
            if not top_like.empty:
                r = top_like.iloc[0]
                lines.append(f"Top post by likes: @{r['username']}:{r['post_id']} ({r['likes']} likes)")
            avg_like = int(df["likes"].mean())
            avg_comments = float(df["comments"].mean())
            lines.append(f"Average likes: {avg_like}")
            lines.append(f"Average comments: {avg_comments:.2f}")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        self.log.info(f"Wrote summary: {path}")
        return path
