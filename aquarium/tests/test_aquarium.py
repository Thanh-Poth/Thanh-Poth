import unittest
import xml.etree.ElementTree as ET

from ascii_aquarium import Config, Repo, build, render
from ascii_aquarium.scene import size_tier, stripes
from ascii_aquarium.species import ART, SIZES, mirror

REPOS = [
    Repo("big-ts", {"TypeScript": 300_000, "CSS": 10_000}),
    Repo("api", {"Python": 50_000, "Dockerfile": 500}),
    Repo("fullstack", {"Python": 50_000, "JavaScript": 40_000}),
    Repo("notes", {"Jupyter Notebook": 400_000}),
    Repo("script", {"Shell": 900}),
    Repo("odd", {"Brainfuck": 3_000}),
    Repo("empty", {}),
    Repo("forked", {"Python": 1000}, fork=True),
    Repo("me", {"Python": 1000}),
]


class SpeciesTest(unittest.TestCase):
    def test_every_species_has_every_size(self):
        for name, sizes in ART.items():
            self.assertEqual(set(sizes), set(SIZES), name)

    def test_mirror_is_an_involution(self):
        for sizes in ART.values():
            for lines in sizes.values():
                self.assertEqual(mirror(mirror(lines)), lines)

    def test_mirror_flips_direction(self):
        self.assertEqual(mirror(["><>"]), ["<><"])


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
        self.assertEqual(species["big-ts"], "tang")
        self.assertEqual(species["api"], "whale")        # Python + Dockerfile combo
        self.assertEqual(species["fullstack"], "ray")    # Python + JS combo
        self.assertEqual(species["notes"], "puffer")
        self.assertEqual(species["script"], "crab")
        self.assertEqual(species["odd"], "goldfish")     # unknown language

    def test_size_tiers_and_weights(self):
        self.assertEqual(size_tier(100, self.cfg), "S")
        self.assertEqual(size_tier(100_000, self.cfg), "M")
        self.assertEqual(size_tier(1_000_000, self.cfg), "L")
        self.assertEqual(self.fish["big-ts"].size, "L")
        self.assertEqual(self.fish["notes"].size, "M")   # notebooks weighted x0.25

    def test_stripes_cover_the_body(self):
        bands = stripes({"A": 3, "B": 1})
        self.assertAlmostEqual(bands[0][1], 0.75)
        self.assertAlmostEqual(bands[-1][1], 1.0)

    def test_deterministic(self):
        again = {f.repo.name: f for f in build(REPOS, self.cfg)}
        for name, f in self.fish.items():
            self.assertEqual((f.y, f.delay, f.facing_right), (again[name].y, again[name].delay,
                                                             again[name].facing_right))

    def test_fish_stay_in_the_tank(self):
        for f in self.fish.values():
            self.assertGreaterEqual(f.y, 0)
            self.assertLessEqual(f.y + f.height, self.cfg.height)


class RenderTest(unittest.TestCase):
    def test_valid_svg_with_one_group_per_fish(self):
        cfg = Config(user="me", highlight=["api"])
        fish = build(REPOS, cfg)
        svg = render(fish, cfg)
        root = ET.fromstring(svg)
        groups = root.findall(".//{http://www.w3.org/2000/svg}g[@class='f']")
        self.assertEqual(len(groups), len(fish))
        self.assertIn("★ api", svg)
        self.assertNotIn("<script", svg)


if __name__ == "__main__":
    unittest.main()
