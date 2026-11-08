"""Minimal GitHub REST client (stdlib only) collecting repos and their languages."""
from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import asdict, dataclass, field

API = "https://api.github.com"


@dataclass
class Repo:
    name: str
    languages: dict[str, int] = field(default_factory=dict)  # language -> bytes of code
    url: str = ""
    fork: bool = False
    archived: bool = False
    stars: int = 0

    @property
    def code_bytes(self) -> int:
        return sum(self.languages.values())

    @property
    def primary_language(self) -> str | None:
        if not self.languages:
            return None
        return max(self.languages.items(), key=lambda kv: kv[1])[0]


def _get(url: str, token: str | None) -> tuple[object, str | None]:
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "ascii-aquarium",
        **({"Authorization": f"Bearer {token}"} if token else {}),
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.load(resp)
        link = resp.headers.get("Link", "")
    next_url = None
    for part in link.split(","):
        if 'rel="next"' in part:
            next_url = part.split(";")[0].strip(" <>")
    return body, next_url


def fetch_repos(user: str, token: str | None = None) -> list[Repo]:
    token = token or os.environ.get("GITHUB_TOKEN") or None
    repos: list[Repo] = []
    url: str | None = f"{API}/users/{user}/repos?per_page=100&type=owner&sort=pushed"
    while url:
        page, url = _get(url, token)
        for r in page:  # type: ignore[union-attr]
            langs, _ = _get(r["languages_url"], token)
            repos.append(Repo(
                name=r["name"],
                languages=dict(langs),  # type: ignore[arg-type]
                url=r["html_url"],
                fork=r["fork"],
                archived=r["archived"],
                stars=r["stargazers_count"],
            ))
    return repos


def dump(repos: list[Repo], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in repos], f, indent=2, ensure_ascii=False)


def load(path: str) -> list[Repo]:
    with open(path, encoding="utf-8") as f:
        return [Repo(**r) for r in json.load(f)]
