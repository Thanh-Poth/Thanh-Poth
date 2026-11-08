"""ASCII species catalogue.

Every species is drawn facing RIGHT (head on the right) in three sizes:
S (small repo), M (medium repo) and L (large repo). Left-facing versions
are derived automatically by :func:`mirror`.

The art is stored in one raw text block so backslashes need no escaping.
A block starts with ``@<species> <size>`` and runs until the next ``@`` line.
"""
from __future__ import annotations

_ART = r"""
@goldfish S
><>
@goldfish M
><(((°>
@goldfish L
   .--~~-.
><(  ((( °>
   '--~~-'
@eel S
~~=°>
@eel M
~~~~~~~~=°>
@eel L
 .~~.   .~~.   .~~.  _
~'  '~~~'  '~~~'  '~=°>
@puffer S
>(°)
@puffer M
  .^^^.
>(  ° )
  'vvv'
@puffer L
   .^^^^^.
 .^  . .  ^.
>(  . .   ° )
 'v  . .  v'
   'vvvvv'
@tang S
}))°>
@tang M
  _/\_
}(  ))°>
  ~\/~
@tang L
    __/\__
|\.'  )))  '.
| >  )))   ° >
|/'.  )))  .'
    ~~\/~~
@angelfish S
>|°>
@angelfish M
  /|
>( °>
  \|
@angelfish L
     /|
    / |
\_./ ))\
/ '\ )) °>
    \ |
     \|
@swordfish S
><>=--
@swordfish M
><((((°>======
@swordfish L
      _/|_
><(((((    °>=========
      `\|`
@whale S
}=__°)
@whale M
     ,'
|\.---._
|/___ °_)
@whale L
         , ' ,
|\    ____.-''-.
| \.-'         o'.
|  ____         _)
|/'    `------''
@ray S
~-<:>
@ray M
   _.-.
~~<  °  >
   `-.-'
@ray L
      _..--.
    .'      '.
~~~<    ° °   >
    '.      .'
      `''--'
@crab S
v(°°)v
@crab M
(\/)  (\/)
 \(°_°)/
  /   \
@crab L
 (\/)     (\/)
  \ \ ___ / /
   \(°   °)/
    /|___|\
   / /   \ \
@jellyfish S
.-.
/|\
@jellyfish M
 .--.
(    )
 '--'
 )(()
 ( )(
@jellyfish L
   .---.
 .'     '.
(  .   .  )
 '-.-.-.-'
  ) ( ) (
 (  ) (  )
  )  (  (
"""

SIZES = ("S", "M", "L")


def _parse(block: str) -> dict[str, dict[str, list[str]]]:
    out: dict[str, dict[str, list[str]]] = {}
    current: list[str] | None = None
    for raw in block.splitlines():
        if raw.startswith("@"):
            name, size = raw[1:].split()
            current = out.setdefault(name, {}).setdefault(size, [])
        elif current is not None and raw.strip():
            current.append(raw.rstrip())
    return {name: {size: _dedent(lines) for size, lines in sizes.items()}
            for name, sizes in out.items()}


def _dedent(lines: list[str]) -> list[str]:
    """Remove the indentation shared by every line, and trailing spaces."""
    indent = min(len(l) - len(l.lstrip(" ")) for l in lines)
    return [l[indent:].rstrip() for l in lines]


ART: dict[str, dict[str, list[str]]] = _parse(_ART)

# Species that crawl on the sand instead of swimming mid-water.
BOTTOM_DWELLERS = {"crab"}
# Species that drift slowly and bob a lot.
DRIFTERS = {"jellyfish"}

# Combination rules, checked in order before the main-language table.
# Each rule: every group must be present with at least `min_share` of the code;
# a group is "A|B" = A or B.
DEFAULT_COMBOS: list[dict] = [
    {"all": ["Python", "JavaScript|TypeScript"], "species": "ray", "min_share": 0.10},
    {"all": ["Python", "Dockerfile"], "species": "whale", "min_share": 0.0},
]

# Primary GitHub language -> species. Unknown languages become goldfish.
DEFAULT_LANGUAGE_SPECIES: dict[str, str] = {
    "Python": "eel",
    "Jupyter Notebook": "puffer",
    "TypeScript": "tang",
    "JavaScript": "angelfish",
    "C": "swordfish",
    "C++": "swordfish",
    "Rust": "swordfish",
    "Go": "swordfish",
    "Java": "swordfish",
    "Dockerfile": "whale",
    "HCL": "whale",
    "Shell": "crab",
    "PowerShell": "crab",
    "Batchfile": "crab",
    "Makefile": "crab",
    "HTML": "jellyfish",
    "CSS": "jellyfish",
    "SCSS": "jellyfish",
    "Vue": "jellyfish",
}
FALLBACK_SPECIES = "goldfish"

_MIRROR = str.maketrans({
    "(": ")", ")": "(", "<": ">", ">": "<", "/": "\\", "\\": "/",
    "[": "]", "]": "[", "{": "}", "}": "{", "`": "'", "'": "`",
    "d": "b", "b": "d", "p": "q", "q": "p",
})


def mirror(lines: list[str]) -> list[str]:
    """Return the left-facing version of right-facing art."""
    width = max(len(line) for line in lines)
    return _dedent([line.ljust(width)[::-1].translate(_MIRROR) for line in lines])


def art(species: str, size: str, facing_right: bool = True) -> list[str]:
    if species not in ART:
        species = FALLBACK_SPECIES
    lines = ART[species][size]
    return list(lines) if facing_right else mirror(lines)
