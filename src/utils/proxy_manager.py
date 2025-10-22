import json
import itertools
from pathlib import Path
from typing import Dict, Optional, Iterator


class ProxyManager:
    def __init__(self, proxies_path: Path, enable_rotation: bool = False):
        self.enable_rotation = enable_rotation
        self._cycle: Optional[Iterator[Dict[str, str]]] = None
        self._load(proxies_path)

    def _load(self, path: Path):
        self._proxies = []
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for entry in data:
                    http = entry.get("http", "").strip()
                    https = entry.get("https", "").strip()
                    if http or https:
                        self._proxies.append({"http": http or None, "https": https or None})
        if self._proxies and self.enable_rotation:
            self._cycle = itertools.cycle(self._proxies)

    def next_proxy(self) -> Optional[Dict[str, str]]:
        if not self._proxies:
            return None
        if self.enable_rotation and self._cycle:
            return next(self._cycle)
        return self._proxies[0]
