# ascii-aquarium

Turns a GitHub profile into an **animated ASCII aquarium** (a single SVG file). Each repository is one fish:

| Fish property | Comes from |
|---|---|
| **Species** | the languages of the repo: combination rules first, then the main language |
| **Colour bands** | the language mix, each band sized by that language's share of the code |
| **Size** | the bytes of code (S / M / L drawing plus continuous font scaling) |
| **Lane, direction, speed** | a hash of the repo name, so the tank stays stable between runs |

No dependencies: Python 3.11+ standard library only.

## Species

| Rule | Species | Look (small → medium) |
|---|---|---|
| Python + JavaScript/TypeScript (≥ 10 % each) | manta ray | `~-<:>` · `~~<  °  >` |
| Python + Dockerfile | whale | `}=__°)` |
| Python | eel | `~~~~~~~~=°>` |
| Jupyter Notebook | pufferfish | `>(°)` |
| TypeScript | tang | `}))°>` |
| JavaScript | angelfish | `>( °>` |
| C, C++, Rust, Go, Java | swordfish | `><((((°>======` |
| Dockerfile, HCL | whale | `}=__°)` |
| Shell, PowerShell, Batch, Makefile | crab (walks on the sand) | `v(°°)v` |
| HTML, CSS, SCSS, Vue | jellyfish (drifts) | `(    )` |
| anything else | goldfish | `><(((°>` |

All drawings face right and are mirrored automatically for fish swimming left.

## Usage

```bash
python -m ascii_aquarium --config aquarium.toml --out dist/aquarium.svg
python -m ascii_aquarium --user octocat --out tank.svg            # no config file
python -m ascii_aquarium --dump-json repos.json                     # save the API data
python -m ascii_aquarium --from-json repos.json --out tank.svg      # render offline
```

Set `GITHUB_TOKEN` to avoid the API rate limit (60 requests per hour without a token; the tool makes one request per repository).

All the options are in [aquarium.toml](aquarium.toml): excluded repos, number of fish, size thresholds, language weights, species overrides, combination rules and highlighted repos.

## How it animates on GitHub

GitHub removes CSS and JavaScript from README files, but an SVG shown through `<img>` keeps its own `<style>` block.
Every fish is a `<g>` with its own `@keyframes` (a horizontal crossing) and an inner group that bobs up and down.
Bubbles, seaweed and light rays are CSS animations too. With `prefers-reduced-motion`, everything stops and each fish stays at a fixed position.

## Tests

```bash
python -m unittest discover -s tests
```
