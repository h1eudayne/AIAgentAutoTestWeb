"""
Unit tests for Screenshot Diff
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from PIL import Image

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.screenshot_diff import ScreenshotDiff


class TestScreenshotDiff(unittest.TestCase):
    """Test ScreenshotDiff class"""

    def setUp(self):
        """Set up test with temp directories"""
        self.temp_dir = tempfile.mkdtemp()
        self.baseline_dir = Path(self.temp_dir) / "baseline"
        self.current_dir = Path(self.temp_dir) / "current"
        self.diff_dir = Path(self.temp_dir) / "diff"

        self.diff = ScreenshotDiff(
            baseline_dir=str(self.baseline_dir),
            current_dir=str(self.current_dir),
            diff_dir=str(self.diff_dir),
        )

    def tearDown(self):
        """Clean up temp directories"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test initialization creates directories"""
        self.assertTrue(self.baseline_dir.exists())
        self.assertTrue(self.current_dir.exists())
        self.assertTrue(self.diff_dir.exists())
        self.assertEqual(self.diff.threshold, 0.1)

    def test_capture_baseline(self):
        """Test capturing baseline screenshot"""
        mock_driver = Mock()
        mock_driver.save_screenshot = Mock(return_value=True)

        filepath = self.diff.capture_baseline(mock_driver, "test_page")

        mock_driver.save_screenshot.assert_called_once()
        self.assertIn("test_page.png", filepath)

    def test_capture_current(self):
        """Test capturing current screenshot"""
        mock_driver = Mock()
        mock_driver.save_screenshot = Mock(return_value=True)

        filepath = self.diff.capture_current(mock_driver, "test_page")

        mock_driver.save_screenshot.assert_called_once()
        self.assertIn("test_page.png", filepath)

    def test_compare_no_baseline(self):
        """Test comparison when baseline doesn't exist"""
        result = self.diff.compare("nonexistent")

        self.assertEqual(result["status"], "no_baseline")
        self.assertEqual(result["mismatch_pixels"], 0)

    def test_compare_no_current(self):
        """Test comparison when current doesn't exist"""
        # Create baseline
        baseline_path = self.baseline_dir / "test.png"
        img = Image.new("RGB", (100, 100), color="red")
        img.save(baseline_path)

        result = self.diff.compare("test")

        self.assertEqual(result["status"], "no_current")

    def test_compare_identical_images(self):
        """Test comparison of identical images"""
        # Create identical images
        baseline_path = self.baseline_dir / "test.png"
        current_path = self.current_dir / "test.png"

        img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 255))
        img.save(baseline_path)
        img.save(current_path)

        result = self.diff.compare("test")

        self.assertEqual(result["status"], "identical")
        self.assertEqual(result["mismatch_pixels"], 0)
        self.assertEqual(result["mismatch_percentage"], 0)

    def test_compare_different_images(self):
        """Test comparison of different images"""
        # Create different images
        baseline_path = self.baseline_dir / "test.png"
        current_path = self.current_dir / "test.png"

        img1 = Image.new("RGBA", (100, 100), color=(255, 0, 0, 255))
        img2 = Image.new("RGBA", (100, 100), color=(0, 255, 0, 255))

        img1.save(baseline_path)
        img2.save(current_path)

        result = self.diff.compare("test")

        self.assertIn(result["status"], ["minor_diff", "moderate_diff", "major_diff"])
        self.assertGreater(result["mismatch_pixels"], 0)
        self.assertGreater(result["mismatch_percentage"], 0)

    def test_compare_different_sizes(self):
        """Test comparison of images with different sizes"""
        # Create images with different sizes
        baseline_path = self.baseline_dir / "test.png"
        current_path = self.current_dir / "test.png"

        img1 = Image.new("RGBA", (100, 100), color=(255, 0, 0, 255))
        img2 = Image.new("RGBA", (150, 150), color=(255, 0, 0, 255))

        img1.save(baseline_path)
        img2.save(current_path)

        # Should resize and compare
        result = self.diff.compare("test")

        self.assertIsNotNone(result["status"])

    def test_get_summary_empty(self):
        """Test summary with no comparisons"""
        summary = self.diff.get_summary()

        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["identical"], 0)

    def test_get_summary_with_results(self):
        """Test summary with comparison results"""
        # Add mock results
        self.diff.comparison_results = [
            {"status": "identical"},
            {"status": "minor_diff"},
            {"status": "major_diff"},
        ]

        summary = self.diff.get_summary()

        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["identical"], 1)
        self.assertEqual(summary["minor_diff"], 1)
        self.assertEqual(summary["major_diff"], 1)

    def test_update_baseline(self):
        """Test updating baseline"""
        # Create current screenshot
        current_path = self.current_dir / "test.png"
        img = Image.new("RGB", (100, 100), color="blue")
        img.save(current_path)

        self.diff.update_baseline("test")

        # Check baseline created
        baseline_path = self.baseline_dir / "test.png"
        self.assertTrue(baseline_path.exists())

    def test_clear_current(self):
        """Test clearing current screenshots"""
        # Create some current screenshots
        for i in range(3):
            path = self.current_dir / f"test{i}.png"
            img = Image.new("RGB", (100, 100))
            img.save(path)

        self.diff.clear_current()

        # Check all cleared
        remaining = list(self.current_dir.glob("*.png"))
        self.assertEqual(len(remaining), 0)

    def test_clear_diff(self):
        """Test clearing diff screenshots"""
        # Create some diff screenshots
        for i in range(3):
            path = self.diff_dir / f"test{i}_diff.png"
            img = Image.new("RGB", (100, 100))
            img.save(path)

        self.diff.clear_diff()

        # Check all cleared
        remaining = list(self.diff_dir.glob("*.png"))
        self.assertEqual(len(remaining), 0)

    def test_save_report(self):
        """Test saving report"""
        # Add some results
        self.diff.comparison_results = [
            {"name": "test1", "status": "identical", "mismatch_percentage": 0},
            {"name": "test2", "status": "minor_diff", "mismatch_percentage": 0.5},
        ]

        filepath = self.diff.save_report("test_report.json")

        # Check file created
        self.assertTrue(Path(filepath).exists())

        # Check content
        import json

        with open(filepath, "r") as f:
            data = json.load(f)

        self.assertIn("summary", data)
        self.assertIn("comparisons", data)


class TestScreenshotDiffIntegration(unittest.TestCase):
    """Integration tests for ScreenshotDiff"""

    def setUp(self):
        """Set up"""
        self.temp_dir = tempfile.mkdtemp()
        self.diff = ScreenshotDiff(
            baseline_dir=str(Path(self.temp_dir) / "baseline"),
            current_dir=str(Path(self.temp_dir) / "current"),
            diff_dir=str(Path(self.temp_dir) / "diff"),
        )

    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_full_workflow(self):
        """Test complete screenshot diff workflow"""
        # Create baseline
        baseline_path = self.diff.baseline_dir / "page.png"
        img1 = Image.new("RGBA", (200, 200), color=(255, 0, 0, 255))
        img1.save(baseline_path)

        # Create current (slightly different)
        current_path = self.diff.current_dir / "page.png"
        img2 = Image.new("RGBA", (200, 200), color=(255, 0, 0, 255))
        # Add a small difference
        for x in range(10):
            for y in range(10):
                img2.putpixel((x, y), (0, 255, 0, 255))
        img2.save(current_path)

        # Compare
        result = self.diff.compare("page", threshold=0.1)

        # Check result
        self.assertIsNotNone(result["status"])
        self.assertGreater(result["mismatch_pixels"], 0)

        # Check diff image created
        diff_path = self.diff.diff_dir / "page_diff.png"
        self.assertTrue(diff_path.exists())

        # Get summary
        summary = self.diff.get_summary()
        self.assertEqual(summary["total"], 1)

        # Save report
        report_path = self.diff.save_report()
        self.assertTrue(Path(report_path).exists())


if __name__ == "__main__":
    unittest.main()
