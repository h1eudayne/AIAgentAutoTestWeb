"""
Unit tests for Self-healing Selector
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from selenium.common.exceptions import NoSuchElementException

from agent.self_healing import SelfHealingSelector


class TestSelfHealingSelector(unittest.TestCase):
    """Test SelfHealingSelector class"""

    def setUp(self):
        """Set up test healer"""
        self.healer = SelfHealingSelector()
        self.mock_driver = Mock()

    def test_initialization(self):
        """Test healer initialization"""
        self.assertIsNotNone(self.healer.healing_history)
        self.assertIsNotNone(self.healer.selector_mappings)
        self.assertEqual(len(self.healer.healing_strategies), 6)

    def test_find_element_success_first_try(self):
        """Test finding element on first try"""
        mock_element = Mock()
        self.mock_driver.find_element.return_value = mock_element

        element, selector = self.healer.find_element(
            self.mock_driver, "#valid-selector", "button"
        )

        self.assertEqual(element, mock_element)
        self.assertEqual(selector, "#valid-selector")

    def test_find_element_with_known_mapping(self):
        """Test finding element with known mapping"""
        # Add known mapping
        self.healer.selector_mappings["#old-id"] = "#new-id"

        # First call fails, second succeeds with mapped selector
        mock_element = Mock()
        self.mock_driver.find_element.side_effect = [
            NoSuchElementException(),  # Original fails
            mock_element,  # Mapped succeeds
        ]

        element, selector = self.healer.find_element(
            self.mock_driver, "#old-id", "button"
        )

        self.assertEqual(element, mock_element)
        self.assertEqual(selector, "#new-id")

    def test_find_element_healing_required(self):
        """Test finding element with healing"""
        # Original selector fails
        mock_element = Mock()

        def find_element_side_effect(*args, **kwargs):
            raise NoSuchElementException()

        self.mock_driver.find_element.side_effect = find_element_side_effect

        # Create a mock strategy that succeeds
        def mock_heal_strategy(driver, selector, element_type):
            return (mock_element, "#healed-id")

        # Replace healing strategies with our mock
        original_strategies = self.healer.healing_strategies
        self.healer.healing_strategies = [mock_heal_strategy]

        try:
            element, selector = self.healer.find_element(
                self.mock_driver, "#broken-selector", "button"
            )

            self.assertEqual(element, mock_element)
            self.assertEqual(selector, "#healed-id")
            self.assertIn("#broken-selector", self.healer.selector_mappings)
        finally:
            self.healer.healing_strategies = original_strategies

    def test_find_element_all_strategies_fail(self):
        """Test when all healing strategies fail"""
        self.mock_driver.find_element.side_effect = NoSuchElementException()

        # Mock all strategies to fail
        for strategy in self.healer.healing_strategies:
            with patch.object(self.healer, strategy.__name__, return_value=None):
                pass

        element, selector = self.healer.find_element(
            self.mock_driver, "#broken-selector", "button"
        )

        self.assertIsNone(element)
        self.assertIsNone(selector)

    def test_heal_by_id(self):
        """Test healing by ID strategy"""
        mock_element = Mock()
        self.mock_driver.find_element.return_value = mock_element

        result = self.healer._heal_by_id(
            self.mock_driver, "button#submit-btn", "button"
        )

        self.assertIsNotNone(result)
        element, selector = result
        self.assertEqual(element, mock_element)
        self.assertEqual(selector, "#submit-btn")

    def test_heal_by_text(self):
        """Test healing by text strategy"""
        # Mock elements with text
        mock_elements = []
        for i in range(3):
            elem = Mock()
            elem.text = f"Button {i}"
            mock_elements.append(elem)

        self.mock_driver.find_elements.return_value = mock_elements
        self.mock_driver.find_element.return_value = mock_elements[0]

        result = self.healer._heal_by_text(
            self.mock_driver, "button:nth-of-type(99)", "button"
        )

        self.assertIsNotNone(result)

    def test_heal_by_attributes(self):
        """Test healing by attributes strategy"""
        # Mock elements with attributes
        mock_element = Mock()
        mock_element.get_attribute.side_effect = lambda attr: {
            "data-testid": "submit-button",
            "name": None,
            "aria-label": None,
        }.get(attr)

        self.mock_driver.find_elements.return_value = [mock_element]
        self.mock_driver.find_element.return_value = mock_element

        result = self.healer._heal_by_attributes(
            self.mock_driver, "button:nth-of-type(99)", "button"
        )

        self.assertIsNotNone(result)

    def test_heal_by_position(self):
        """Test healing by position strategy"""
        # Mock elements
        mock_elements = [Mock() for _ in range(3)]
        for elem in mock_elements:
            elem.is_displayed.return_value = True
            elem.is_enabled.return_value = True

        self.mock_driver.find_elements.return_value = mock_elements
        self.mock_driver.find_element.return_value = mock_elements[0]

        result = self.healer._heal_by_position(
            self.mock_driver, "button.old-class", "button"
        )

        self.assertIsNotNone(result)

    def test_heal_by_similarity(self):
        """Test healing by similarity strategy"""
        # Mock element with similar classes
        mock_element = Mock()
        mock_element.get_attribute.return_value = "btn btn-primary submit"

        self.mock_driver.find_elements.return_value = [mock_element]

        result = self.healer._heal_by_similarity(
            self.mock_driver, "button.btn.btn-primary", "button"  # Use matching class
        )

        self.assertIsNotNone(result)

    def test_heal_by_parent_context(self):
        """Test healing by parent context strategy"""
        # Mock parent and child elements
        mock_parent = Mock()
        mock_child = Mock()
        mock_child.is_displayed.return_value = True

        mock_parent.find_elements.return_value = [mock_child]
        self.mock_driver.find_element.return_value = mock_parent

        result = self.healer._heal_by_parent_context(
            self.mock_driver, "button.old-class", "button"
        )

        self.assertIsNotNone(result)

    def test_get_healing_stats_empty(self):
        """Test healing stats when empty"""
        stats = self.healer.get_healing_stats()

        self.assertEqual(stats["total_healings"], 0)
        self.assertEqual(stats["unique_selectors_healed"], 0)

    def test_get_healing_stats_with_data(self):
        """Test healing stats with data"""
        # Add healing history
        self.healer.healing_history = [
            {"strategy": "_heal_by_id"},
            {"strategy": "_heal_by_text"},
            {"strategy": "_heal_by_id"},
        ]
        self.healer.selector_mappings = {"#old1": "#new1", "#old2": "#new2"}

        stats = self.healer.get_healing_stats()

        self.assertEqual(stats["total_healings"], 3)
        self.assertEqual(stats["unique_selectors_healed"], 2)
        self.assertEqual(stats["strategies_used"]["_heal_by_id"], 2)
        self.assertEqual(stats["most_effective_strategy"], "_heal_by_id")

    def test_get_selector_mapping(self):
        """Test getting selector mapping"""
        self.healer.selector_mappings["#old"] = "#new"

        result = self.healer.get_selector_mapping("#old")
        self.assertEqual(result, "#new")

        result = self.healer.get_selector_mapping("#nonexistent")
        self.assertIsNone(result)

    def test_export_mappings(self):
        """Test exporting selector mappings"""
        # Add some data
        self.healer.selector_mappings = {"#old": "#new"}
        self.healer.healing_history = [{"strategy": "_heal_by_id"}]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_file = f.name

        try:
            self.healer.export_mappings(temp_file)

            # Check file created
            self.assertTrue(Path(temp_file).exists())

            # Check content
            with open(temp_file, "r") as f:
                data = json.load(f)

            self.assertIn("mappings", data)
            self.assertIn("history", data)
            self.assertIn("stats", data)

        finally:
            Path(temp_file).unlink()

    def test_import_mappings(self):
        """Test importing selector mappings"""
        # Create temp file with mappings
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_file = f.name
            json.dump(
                {"mappings": {"#old1": "#new1", "#old2": "#new2"}, "history": []}, f
            )

        try:
            self.healer.import_mappings(temp_file)

            # Check mappings imported
            self.assertEqual(len(self.healer.selector_mappings), 2)
            self.assertEqual(self.healer.selector_mappings["#old1"], "#new1")

        finally:
            Path(temp_file).unlink()


class TestSelfHealingIntegration(unittest.TestCase):
    """Integration tests for SelfHealingSelector"""

    def setUp(self):
        """Set up"""
        self.healer = SelfHealingSelector()
        self.mock_driver = Mock()

    def test_full_healing_workflow(self):
        """Test complete healing workflow"""
        # Simulate broken selector that needs healing
        mock_element = Mock()

        # Original selector fails, healed selector succeeds
        def find_element_side_effect(by, selector):
            if selector == "#broken-id":
                raise NoSuchElementException()
            return mock_element

        self.mock_driver.find_element.side_effect = find_element_side_effect

        # Create a mock strategy that succeeds
        def mock_heal_strategy(driver, selector, element_type):
            return (mock_element, "#healed-id")

        # Replace healing strategies with our mock
        original_strategies = self.healer.healing_strategies
        self.healer.healing_strategies = [mock_heal_strategy]

        try:
            # First attempt
            element1, selector1 = self.healer.find_element(
                self.mock_driver, "#broken-id", "button"
            )

            self.assertEqual(element1, mock_element)
            self.assertEqual(selector1, "#healed-id")

            # Second attempt should use mapping
            element2, selector2 = self.healer.find_element(
                self.mock_driver, "#broken-id", "button"
            )

            self.assertEqual(element2, mock_element)
            self.assertEqual(selector2, "#healed-id")

            # Check stats
            stats = self.healer.get_healing_stats()
            self.assertGreater(stats["total_healings"], 0)
        finally:
            self.healer.healing_strategies = original_strategies

        # Export and import
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_file = f.name

        try:
            self.healer.export_mappings(temp_file)

            # Create new healer and import
            new_healer = SelfHealingSelector()
            new_healer.import_mappings(temp_file)

            # Check mapping imported
            self.assertEqual(
                new_healer.get_selector_mapping("#broken-id"), "#healed-id"
            )

        finally:
            Path(temp_file).unlink()


if __name__ == "__main__":
    unittest.main()
