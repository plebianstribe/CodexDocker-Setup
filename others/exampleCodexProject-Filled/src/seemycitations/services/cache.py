from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any


class JsonCache:
    def __init__(self, root: Path, *, ttl_seconds: int = 86400):
        self.root = root
        self.ttl_seconds = ttl_seconds
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, namespace: str, key: str) -> Path:
        digest = hashlib.sha256(key.encode()).hexdigest()
        target = self.root / namespace
        target.mkdir(parents=True, exist_ok=True)
        return target / f"{digest}.json"

    def get(self, namespace: str, key: str) -> Any | None:
        path = self._path(namespace, key)
        if not path.exists():
            return None
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if time.time() - record.get("stored_at", 0) > self.ttl_seconds:
            return None
        return record.get("value")

    def set(self, namespace: str, key: str, value: Any) -> None:
        path = self._path(namespace, key)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps({"stored_at": time.time(), "value": value}, ensure_ascii=False),
            encoding="utf-8",
        )
        temporary.replace(path)
