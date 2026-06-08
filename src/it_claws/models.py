from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


@dataclass(frozen=True)
class ScrapeTarget:
    name: str
    resolver_type: Literal["static", "dynamic"]
    resolver: Callable[..., Any]
    resolver_kwargs: dict[str, Any]
    file_type: Literal["exe", "zip", "zip/exe", "zip/folder", "sfx"]
    include_cookies: list[str] | None = None
    request_headers: dict[str, str] | None = None
    rename_as: str | None = None
    default_folder: str | None = None
    random_ua: bool = True


@dataclass
class DownloadJob:
    target: ScrapeTarget
    output_root: Path
    custom_folder: str | None = None

    @property
    def destination_directory(self) -> Path:
        if self.custom_folder:
            return self.output_root / self.custom_folder
        return self.output_root / self.target.default_folder / self.target.name
