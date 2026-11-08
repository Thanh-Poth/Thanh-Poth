# ascii-aquarium

Turns a GitHub profile into an **animated ASCII ocean seen from above** (a single SVG file). Each repository is one sea animal:

| Property | Comes from |
|---|---|
| **Species** | the repo's languages: combination rules first, then the main language |
| **Size** | the bytes of code (sprite length grows with the log of the size) |
| **Swimming** | 12 cross-faded ASCII frames per cycle: rays flap their wings, sharks sway their tails, turtles paddle |
| **Path, direction, speed** | a hash of the repo name, so the scene stays stable between runs |

The library itself only needs the Python 3.11+ standard library.

## Species

The silhouettes come from [assets/silhouettes.png](assets/silhouettes.png) (top-down view).

| Rule | Animal | Motion |
|---|---|---|
| Python + JavaScript/TypeScript (≥ 10 % each) | hammerhead shark | tail sway |
| Python + Dockerfile, Dockerfile, Shell, HCL | hammerhead shark | tail sway |
| Python, R, Julia | manta ray (3 silhouette variants) | wing flap |
| TypeScript, JavaScript, C, C++, Rust, Go, Java | shark | tail sway |
| Jupyter Notebook, anything else | sea turtle (hexagon shell) | flipper paddle |

## How the ASCII is made

1. `tools/extract_silhouettes.py` (needs Pillow, NumPy and SciPy, run once) cuts each silhouette out of the image, rotates it so the head points right, and stores it as a run-length mask in `ascii_aquarium/silhouettes.txt`.
2. For each animation frame, `sprite.py` deforms the mask (wing span shrinking, a travelling wave along the body, flippers sweeping), then samples every character cell 4 × 6 times:
   - fully inside → the species texture (`:` ray, `=` hammerhead, `#` shark, hexagons for the turtle);
   - on the outline → `/ \ ( ) _ -`, chosen from the direction of the edge;
   - thin parts (the ray's tail) → `-` or `|`.
3. `render.py` stacks the frames in the SVG and shows one at a time with CSS, while the whole animal crosses the scene on a curved path: smooth wandering (species-specific amplitude and number of turns), the body banking along the tangent, and a speed that surges and glides.

To use your own drawings: replace the image, update `SHAPES` in the tool (position and rotation of each silhouette), run it again, and add the species to `species.py`.

## Usage

```bash
python -m ascii_aquarium --config aquarium.toml --out dist/aquarium.svg --html dist/index.html
python -m ascii_aquarium --user octocat --out ocean.svg             # no config file
python -m ascii_aquarium --dump-json repos.json                     # save the API data
python -m ascii_aquarium --from-json repos.json --out ocean.svg     # render offline
```

Set `GITHUB_TOKEN` to avoid the API rate limit (60 requests per hour without a token; the tool makes one request per repository).

All the options are in [aquarium.toml](aquarium.toml): excluded repos, number of animals, sprite sizes, frames per cycle, language weights, species overrides, combination rules and highlighted repos.

## Two outputs

- `--out aquarium.svg`: the README image. GitHub removes CSS and JavaScript from README files, but an SVG shown through `<img>` keeps its own `<style>` block, so it animates. Images are not interactive on GitHub, so it shows no text; its edges fade out so it blends into the page.
- `--html index.html`: a full-screen page (for GitHub Pages) with the ocean as a real background and the `page_html` card from the config on top. Hovering an animal pauses it and shows the project name; clicking opens the repository.

All animals share one colour (`fish_color`). Depth comes from blurred shadows on the sea floor, drifting light patches, plankton and distant schools of tiny fish. With `prefers-reduced-motion`, everything stops on the first frame.

## Tests

```bash
python -m unittest discover -s tests
```
