from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReleasePackageContractTests(unittest.TestCase):
    def test_required_player_files_exist(self):
        for relative in (
            "VERSION",
            "RELEASE_NOTES.md",
            "packaging/release/START_HERE.txt",
            "packaging/release/input.ini",
            "tools/package_release.ps1",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_packager_guards_private_and_retail_state(self):
        script = (ROOT / "tools/package_release.ps1").read_text(encoding="utf-8")
        for marker in (
            '"*.cue"',
            '-Filter "*.bin"',
            '"*.mcd"',
            '"disc.cfg"',
            '"settings.toml"',
            '"overlay_captures.json"',
            '"psx_freeze_dump_*.json"',
        ):
            self.assertIn(marker, script)

    def test_release_mapping_supports_dpad_and_left_stick(self):
        mapping = (ROOT / "packaging/release/input.ini").read_text(encoding="ascii")
        self.assertIn("up = dpup,lefty-", mapping)
        self.assertIn("down = dpdown,lefty+", mapping)
        self.assertIn("left = dpleft,leftx-", mapping)
        self.assertIn("right = dpright,leftx+", mapping)


if __name__ == "__main__":
    unittest.main()
