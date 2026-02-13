"""
Unit tests for Coverage Tracker
"""

import unittest
from pathlib import Path
import sys
import tempfile
import shutil
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.coverage_tracker import CoverageTracker


class TestCoverageTracker(unittest.TestCase):
    """Test CoverageTracker class"""

    def setUp(self):
        """Set up test tracker"""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = CoverageTracker(output_dir=self.temp_dir)

    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test tracker initialization"""
        self.assertIsNotNone(self.tracker.pages_tested)
        self.assertIsNotNone(self.tracker.elements_tested)
        self.assertIsNotNone(self.tracker.actions_tested)
        self.assertTrue(Path(self.temp_dir).exists())

    def test_set_coverage_goals(self):
        """Test setting coverage goals"""
        pages = ["https://example.com", "https://example.com/about"]
        features = ["login", "search"]
        elements = ["#submit", ".search-btn"]

        self.tracker.set_coverage_goals(
            pages=pages, features=features, critical_elements=elements
        )

        self.assertEqual(len(self.tracker.coverage_goals["pages"]), 2)
        self.assertEqual(len(self.tracker.coverage_goals["features"]), 2)
        self.assertEqual(len(self.tracker.coverage_goals["critical_elements"]), 2)

    def test_track_page(self):
        """Test tracking page"""
        url = "https://example.com"

        self.tracker.track_page(url)

        self.assertIn(url, self.tracker.pages_tested)

    def test_track_element(self):
        """Test tracking element"""
        page = "https://example.com"
        selector = "#submit-btn"

        self.tracker.track_element(page, selector, "click", True)

        self.assertIn(selector, self.tracker.elements_tested[page])
        self.assertEqual(self.tracker.actions_tested[page]["click"], 1)

    def test_track_element_success_rate(self):
        """Test tracking element success rate"""
        page = "https://example.com"
        selector = "#submit-btn"

        # Track successes and failures
        self.tracker.track_element(page, selector, "click", True)
        self.tracker.track_element(page, selector, "click", True)
        self.tracker.track_element(page, selector, "click", False)

        key = f"{page}::{selector}"
        self.assertEqual(self.tracker.element_success_rate[key]["success"], 2)
        self.assertEqual(self.tracker.element_success_rate[key]["fail"], 1)

    def test_track_feature(self):
        """Test tracking feature"""
        feature = "login"

        self.tracker.track_feature(feature)

        self.assertIn(feature, self.tracker.features_tested)

    def test_track_test_result(self):
        """Test tracking complete test result"""
        self.tracker.track_test_result(
            test_name="Test login",
            page="https://example.com",
            elements_tested=["#username", "#password", "#submit"],
            actions=["type", "type", "click"],
            success=True,
        )

        self.assertEqual(len(self.tracker.test_results), 1)
        self.assertIn("https://example.com", self.tracker.pages_tested)

    def test_get_page_coverage_no_goals(self):
        """Test page coverage without goals"""
        self.tracker.track_page("https://example.com")

        coverage = self.tracker.get_page_coverage()

        self.assertEqual(coverage["total_pages_tested"], 1)
        self.assertEqual(coverage["coverage_percentage"], 100)

    def test_get_page_coverage_with_goals(self):
        """Test page coverage with goals"""
        self.tracker.set_coverage_goals(
            pages=["https://example.com", "https://example.com/about"]
        )

        self.tracker.track_page("https://example.com")

        coverage = self.tracker.get_page_coverage()

        self.assertEqual(coverage["goal_pages"], 2)
        self.assertEqual(coverage["goal_pages_tested"], 1)
        self.assertEqual(coverage["coverage_percentage"], 50.0)

    def test_get_element_coverage(self):
        """Test element coverage"""
        self.tracker.track_element("https://example.com", "#btn1", "click", True)
        self.tracker.track_element("https://example.com", "#btn2", "click", True)
        self.tracker.track_element("https://example.com", "#btn3", "click", False)

        coverage = self.tracker.get_element_coverage()

        self.assertEqual(coverage["total_elements_tested"], 3)
        self.assertEqual(coverage["total_attempts"], 3)
        self.assertAlmostEqual(coverage["element_success_rate"], 66.7, places=1)

    def test_get_action_coverage(self):
        """Test action coverage"""
        page = "https://example.com"

        self.tracker.track_element(page, "#btn1", "click", True)
        self.tracker.track_element(page, "#btn2", "click", True)
        self.tracker.track_element(page, "#input1", "type", True)

        coverage = self.tracker.get_action_coverage()

        self.assertEqual(coverage["total_actions"], 3)
        self.assertEqual(coverage["action_types"], 2)
        self.assertEqual(coverage["actions_breakdown"]["click"], 2)
        self.assertEqual(coverage["actions_breakdown"]["type"], 1)

    def test_get_feature_coverage(self):
        """Test feature coverage"""
        self.tracker.set_coverage_goals(features=["login", "search", "checkout"])

        self.tracker.track_feature("login")
        self.tracker.track_feature("search")

        coverage = self.tracker.get_feature_coverage()

        self.assertEqual(coverage["goal_features"], 3)
        self.assertEqual(coverage["goal_features_tested"], 2)
        self.assertAlmostEqual(coverage["coverage_percentage"], 66.7, places=1)

    def test_get_overall_coverage(self):
        """Test overall coverage calculation"""
        # Set goals
        self.tracker.set_coverage_goals(
            pages=["https://example.com"], features=["login"]
        )

        # Track some tests
        self.tracker.track_page("https://example.com")
        self.tracker.track_feature("login")
        self.tracker.track_element("https://example.com", "#btn", "click", True)

        overall = self.tracker.get_overall_coverage()

        self.assertIn("overall_score", overall)
        self.assertIn("page_coverage", overall)
        self.assertIn("feature_coverage", overall)
        self.assertGreater(overall["overall_score"], 0)

    def test_get_coverage_gaps(self):
        """Test identifying coverage gaps"""
        # Set goals
        self.tracker.set_coverage_goals(
            pages=["https://example.com", "https://example.com/about"],
            features=["login", "search"],
        )

        # Track partial coverage
        self.tracker.track_page("https://example.com")
        self.tracker.track_feature("login")

        # Track failing element
        self.tracker.track_element("https://example.com", "#bad-btn", "click", False)
        self.tracker.track_element("https://example.com", "#bad-btn", "click", False)

        gaps = self.tracker.get_coverage_gaps()

        self.assertIn("https://example.com/about", gaps["untested_pages"])
        self.assertIn("search", gaps["untested_features"])
        self.assertGreater(len(gaps["failing_elements"]), 0)

    def test_save_report(self):
        """Test saving coverage report"""
        # Add some data
        self.tracker.track_page("https://example.com")
        self.tracker.track_element("https://example.com", "#btn", "click", True)

        filepath = self.tracker.save_report("test_coverage.json")

        # Check file created
        self.assertTrue(Path(filepath).exists())

        # Check content
        with open(filepath, "r") as f:
            data = json.load(f)

        self.assertIn("summary", data)
        self.assertIn("page_coverage", data)
        self.assertIn("element_coverage", data)


class TestCoverageTrackerIntegration(unittest.TestCase):
    """Integration tests for CoverageTracker"""

    def setUp(self):
        """Set up"""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = CoverageTracker(output_dir=self.temp_dir)

    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_full_coverage_workflow(self):
        """Test complete coverage tracking workflow"""
        # Set goals
        self.tracker.set_coverage_goals(
            pages=["https://example.com", "https://example.com/about"],
            features=["login", "search", "checkout"],
            critical_elements=["#submit", ".search-btn"],
        )

        # Simulate testing
        # Test 1: Homepage
        self.tracker.track_test_result(
            test_name="Test homepage",
            page="https://example.com",
            elements_tested=["#submit", ".nav-link"],
            actions=["click", "click"],
            success=True,
        )

        # Test 2: About page
        self.tracker.track_test_result(
            test_name="Test about",
            page="https://example.com/about",
            elements_tested=[".contact-btn"],
            actions=["click"],
            success=True,
        )

        # Test 3: Failed test
        self.tracker.track_test_result(
            test_name="Test search",
            page="https://example.com",
            elements_tested=[".search-btn"],
            actions=["click"],
            success=False,
        )

        # Track features
        self.tracker.track_feature("login")
        self.tracker.track_feature("search")

        # Get overall coverage
        overall = self.tracker.get_overall_coverage()

        # Verify results
        self.assertEqual(overall["total_tests"], 3)
        self.assertGreater(overall["overall_score"], 0)

        # Check page coverage
        page_cov = self.tracker.get_page_coverage()
        self.assertEqual(page_cov["goal_pages_tested"], 2)
        self.assertEqual(page_cov["coverage_percentage"], 100.0)

        # Check feature coverage
        feature_cov = self.tracker.get_feature_coverage()
        self.assertEqual(feature_cov["goal_features_tested"], 2)
        self.assertAlmostEqual(feature_cov["coverage_percentage"], 66.7, places=1)

        # Check gaps
        gaps = self.tracker.get_coverage_gaps()
        self.assertIn("checkout", gaps["untested_features"])

        # Save report
        report_path = self.tracker.save_report()
        self.assertTrue(Path(report_path).exists())


if __name__ == "__main__":
    unittest.main()
