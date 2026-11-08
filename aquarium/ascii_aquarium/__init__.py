"""ascii_aquarium: turn a GitHub profile into an animated ASCII ocean (SVG).

Each repository becomes a sea animal seen from above (silhouettes in assets/):
  * species  <- languages       (combination rules, then the main language)
  * colours  <- language mix    (bands proportional to bytes per language)
  * size     <- amount of code  (sprite length grows with log(bytes))
  * swimming <- frame-by-frame  (rays flap, sharks sway, turtles paddle)
"""
from .github import Repo, fetch_repos
from .render import render
from .scene import Config, Fish, build

__version__ = "0.1.0"
__all__ = ["Config", "Fish", "Repo", "build", "fetch_repos", "render", "generate"]


def generate(cfg: Config, repos: list[Repo] | None = None) -> str:
    """Fetch (unless given) the repos and return the SVG document."""
    if repos is None:
        repos = fetch_repos(cfg.user)
    return render(build(repos, cfg), cfg)
