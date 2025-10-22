from pathlib import Path
import pandas as pd
from src.exporter import DataExporter


def test_export_json_and_csv(tmp_path):
    df = pd.DataFrame(
        [
            {
                "username": "u",
                "post_id": "1",
                "content": "c",
                "media_url": None,
                "likes": 1,
                "comments": 0,
                "posted_at": "2025-01-01T00:00:00Z",
                "link": "http://x",
                "hashtags": "a,b",
                "mentions": "",
            }
        ]
    )
    exp = DataExporter(output_dir=tmp_path)
    jpath = exp.export_json(df, "t.json")
    cpath = exp.export_csv(df, "t.csv")
    spath = exp.export_summary(df, "t.txt")
    assert Path(jpath).exists()
    assert Path(cpath).exists()
    assert Path(spath).exists()
