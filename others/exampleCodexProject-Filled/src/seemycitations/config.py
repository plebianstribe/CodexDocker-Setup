from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path = Path(os.getenv("SEEMYCITATIONS_DATA_DIR", "data"))
    openalex_email: str | None = os.getenv("OPENALEX_EMAIL")
    max_upload_mb: int = int(os.getenv("SEEMYCITATIONS_MAX_UPLOAD_MB", "25"))

    @property
    def cache_dir(self) -> Path:
        return self.data_dir / "cache"

    @property
    def upload_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def author_dir(self) -> Path:
        return self.data_dir / "authors"


settings = Settings()
