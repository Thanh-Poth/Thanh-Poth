"""ascii_aquarium: turn a GitHub profile into an animated ASCII aquarium (SVG).

Each repository becomes a fish:
  * species  <- main language   (see species.DEFAULT_LANGUAGE_SPECIES)
  * colours  <- language mix    (bands proportional to bytes per language)
  * size     <- amount of code  (S / M / L art + continuous font scaling)
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
