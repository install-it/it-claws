from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


@dataclass(frozen=True)
class ScrapeTarget:
    name: str
    path: str
    resolver_type: Literal["static", "dynamic"]
    resolver: Callable[..., Any]
    file_type: Literal["exe", "zip", "zip/exe", "zip/folder", "sfx"]
    resolver_kwargs: dict[str, Any] = field(default_factory=dict)
    include_cookies: list[str] | None = None
    request_headers: dict[str, str] | None = None
    rename_as: str | None = None
    random_ua: bool = True


@dataclass(frozen=True)
class TargetGroup:
    name: str
    path: str
    members: list[ScrapeTarget]


@dataclass
class DownloadJob:
    target: ScrapeTarget
    output_root: Path
    name: str | None = None

    @property
    def display_name(self) -> str:
        return self.name or self.target.name

    @property
    def destination_directory(self) -> Path:
        resolved = self.target.path.format(name=self.target.name)
        return self.output_root / resolved
