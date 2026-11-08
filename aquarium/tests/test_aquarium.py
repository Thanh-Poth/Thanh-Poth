import unittest
import xml.etree.ElementTree as ET

from ascii_aquarium import Config, Repo, build, render
from ascii_aquarium.scene import stripes
from ascii_aquarium.species import SPECIES, mirror
from ascii_aquarium.sprite import MOTIONS, frames, masks

REPOS = [
    Repo("big-ts", {"TypeScript": 300_000, "CSS": 10_000}),
    Repo("api", {"Python": 50_000, "Dockerfile": 500}),
    Repo("fullstack", {"Python": 50_000, "JavaScript": 40_000}),
    Repo("pipeline", {"Python": 30_000}),
    Repo("notes", {"Jupyter Notebook": 400_000}),
    Repo("odd", {"Brainfuck": 3_000}),
    Repo("empty", {}),
    Repo("forked", {"Python": 1000}, fork=True),
    Repo("me", {"Python": 1000}),
]


class SpriteTest(unittest.TestCase):
    def test_every_species_has_its_silhouettes(self):
        for name, spec in SPECIES.items():
            self.assertIn(spec.motion, MOTIONS, name)
            for m in spec.masks:
                self.assertIn(m, masks(), name)

    def test_frames_share_one_bounding_box_and_move(self):
        for spec in SPECIES.values():
            fr = frames(spec.masks[0], spec.motion, 24, 8, spec.texture)
            self.assertEqual(len(fr), 8)
            self.assertEqual(len({(len(f), len(f[0])) for f in fr}), 1)
            self.assertGreater(len({tuple(f) for f in fr}), 1, spec.masks[0])  # it swims

    def test_bigger_repo_bigger_sprite(self):
        small = frames("shark", "sway", 12, 2, "#")[0]
        big = frames("shark", "sway", 36, 2, "#")[0]
        self.assertGreater(len(big[0]), len(small[0]))
        self.assertGreater(len(big), len(small))

    def test_mirror_is_an_involution(self):
        fr = frames("ray1", "flap", 24, 1, ":")[0]
        self.assertEqual(mirror(mirror(fr)), fr)


class SceneTest(unittest.TestCase):
    def setUp(self):
        self.cfg = Config(user="me")
        self.fish = {f.repo.name: f for f in build(REPOS, self.cfg)}

    def test_selection(self):
        self.assertNotIn("empty", self.fish)
        self.assertNotIn("forked", self.fish)
        self.assertNotIn("me", self.fish)  # profile repo excluded

    def test_species_rules(self):
        species = {n: f.species for n, f in self.fish.items()}
        self.assertEqual(species["big-ts"], "shark")
        self.assertEqual(species["api"], "hammerhead")        # Python + Dockerfile combo
        self.assertEqual(species["fullstack"], "hammerhead")  # Python + JS combo
        self.assertEqual(species["pipeline"], "ray")
        self.assertEqual(species["notes"], "turtle")
        self.assertEqual(species["odd"], "turtle")            # unknown language

    def test_size_follows_code_and_weights(self):
        self.assertLess(self.cfg.cols_for(1_000), self.cfg.cols_for(100_000))
        self.assertEqual(self.cfg.cols_for(10), self.cfg.min_cols)
        self.assertEqual(self.cfg.cols_for(10**9), self.cfg.max_cols)
        self.assertEqual(self.cfg.size_bytes(REPOS[4]), 100_000)  # notebooks weighted x0.25

    def test_stripes_cover_the_body(self):
        bands = stripes({"A": 3, "B": 1})
        self.assertAlmostEqual(bands[0][1], 0.75)
        self.assertAlmostEqual(bands[-1][1], 1.0)

    def test_deterministic(self):
        again = {f.repo.name: f for f in build(REPOS, self.cfg)}
        for name, f in self.fish.items():
            g = again[name]
            self.assertEqual((f.y0, f.y1, f.delay, f.facing_right, f.frames),
                             (g.y0, g.y1, g.delay, g.facing_right, g.frames))

    def test_animals_stay_in_the_scene(self):
        for f in self.fish.values():
            for y in (f.y0, f.y1):
                self.assertGreaterEqual(y, 0)
                self.assertLessEqual(y + f.height, self.cfg.height)


class RenderTest(unittest.TestCase):
    def test_valid_svg_with_frames(self):
        cfg = Config(user="me", highlight=["api"])
        fish = build(REPOS, cfg)
        svg = render(fish, cfg)
        root = ET.fromstring(svg)
        ns = "{http://www.w3.org/2000/svg}"
        self.assertEqual(len(root.findall(f".//{ns}g[@class='f']")), len(fish))
        frame_groups = [g for g in root.iter(f"{ns}g") if g.get("class", "").startswith("fr")]
        self.assertEqual(len(frame_groups), len(fish) * cfg.frames)
        self.assertIn("★ api", svg)
        self.assertNotIn("<script", svg)


if __name__ == "__main__":
    unittest.main()
