import tempfile
import unittest
from pathlib import Path

from gen_image import make_background


class LocalBackgroundTests(unittest.TestCase):
    def test_make_background_creates_png_without_network(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "bg.png"
            result = make_background("cozy dusk", out_path, 1080, 1350)
            self.assertEqual(result, str(out_path))
            self.assertTrue(out_path.exists())
            self.assertTrue(out_path.stat().st_size > 0)


if __name__ == "__main__":
    unittest.main()
