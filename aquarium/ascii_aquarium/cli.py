"""Command line: python -m ascii_aquarium --config aquarium.toml --out dist/aquarium.svg"""
from __future__ import annotations

import argparse
import os

from . import github
from .render import render
from .scene import Config, build


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ascii_aquarium", description=__doc__)
    p.add_argument("--config", default="aquarium.toml", help="TOML config file")
    p.add_argument("--user", help="GitHub user (overrides the config)")
    p.add_argument("--out", default="dist/aquarium.svg", help="output SVG path")
    p.add_argument("--from-json", help="render from a saved repo dump instead of the API")
    p.add_argument("--dump-json", help="also save the fetched repos to this JSON file")
    args = p.parse_args(argv)

    if os.path.exists(args.config):
        cfg = Config.load(args.config)
        if args.user:
            cfg.user = args.user
    elif args.user:
        cfg = Config(user=args.user)
    else:
        p.error(f"config file {args.config!r} not found and no --user given")

    repos = github.load(args.from_json) if args.from_json else github.fetch_repos(cfg.user)
    if args.dump_json:
        github.dump(repos, args.dump_json)
    fish = build(repos, cfg)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(render(fish, cfg))
    for fi in fish:
        print(f"{fi.repo.name:42} {fi.species:10} {fi.mask:10} {len(fi.frames[0][0]):>3} cols "
              f"{cfg.size_bytes(fi.repo):>9} B  {fi.repo.primary_language}")
    print(f"wrote {args.out} ({len(fish)} fish)")
    return 0
