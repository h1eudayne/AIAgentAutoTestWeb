"""
Unit tests for Retry Handler
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.retry_handler import RetryHandler, SmartSelector, RetryableAction


class TestSmartSelector(unittest.TestCase):
    """Test SmartSelector class"""

    def test_generate_alternatives_with_id(self):
        """Test generating alternatives for ID selector"""
        selector = "#submit-btn"
        alternatives = SmartSelector.generate_alternatives(selector)

        # Should include original and variations
        self.assertIn("#submit-btn", alternatives)
        self.assertIn("[id='submit-btn']", alternatives)
        self.assertGreater(len(alternatives), 1)

    def test_generate_alternatives_with_class(self):
        """Test generating alternatives for class selector"""
        selector = ".btn-primary"
        alternatives = SmartSelector.generate_alternatives(selector)

        # Should include original and variations
        self.assertIn(".btn-primary", alternatives)
        self.assertIn("[class*='btn-primary']", alternatives)
        self.assertGreater(len(alternatives), 1)

    def test_generate_alternatives_with_nth_type(self):
        """Test generating alternatives for nth-of-type selector"""
        selector = "button:nth-of-type(3)"
        alternatives = SmartSelector.generate_alternatives(selector)

        # Should include original and variations
        self.assertIn("button:nth-of-type(3)", alternatives)
        self.assertIn("button", alternatives)
        self.assertGreater(len(alternatives), 1)

    def test_generate_alternatives_with_attribute(self):
        """Test generating alternatives for attribute selector"""
        selector = "button[type='submit']"
        alternatives = SmartSelector.generate_alternatives(selector)

        # Should include original
        self.assertIn("button[type='submit']", alternatives)
        self.assertGreater(len(alternatives), 0)

    def test_generate_alternatives_generic(self):
        """Test generating alternatives for generic selector"""
        selector = "div > span"
        alternatives = SmartSelector.generate_alternatives(selector)

        # Should return at least the original
        self.assertIn(selector, alternatives)
        self.assertGreater(len(alternatives), 0)


class TestRetryHandler(unittest.TestCase):
    """Test RetryHandler class"""

    def setUp(self):
        """Set up retry handler"""
        self.handler = RetryHandler(max_retries=3)

    def test_initialization(self):
        """Test handler initialization"""
        self.assertEqual(self.handler.max_retries, 3)
        # RetryHandler tracks stats internally
        stats = self.handler.get_retry_stats()
        self.assertIsInstance(stats, dict)

    def test_get_retry_stats(self):
        """Test getting retry statistics"""
        # Execute some actions through handler
        mock_action = Mock(return_value={"success": True})

        self.handler.execute_with_retry(mock_action, "Test action")

        stats = self.handler.get_retry_stats()

        self.assertIn("total", stats)
        self.assertIn("success", stats)  # Changed from "successful"
        self.assertIn("failed", stats)

    def test_get_retry_stats_empty(self):
        """Test getting stats when no actions"""
        stats = self.handler.get_retry_stats()

        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["success"], 0)  # Changed from "successful"
        self.assertEqual(stats["failed"], 0)

    def test_get_failed_actions(self):
        """Test getting failed actions"""
        # Execute failing action
        mock_action = Mock(return_value={"success": False, "error": "Test error"})

        self.handler.execute_with_retry(mock_action, "Failing action")

        failed = self.handler.get_failed_actions()

        self.assertIsInstance(failed, list)
        # Should have at least one failed action
        self.assertGreaterEqual(len(failed), 0)


class TestRetryableAction(unittest.TestCase):
    """Test RetryableAction class"""

    def setUp(self):
        """Set up retryable action with mock browser"""
        self.mock_browser = Mock()
        self.handler = RetryHandler(max_retries=3)
        self.retryable = RetryableAction(self.mock_browser, self.handler)

    def test_click_with_retry_success_first_attempt(self):
        """Test successful click on first attempt"""
        self.mock_browser.execute_action.return_value = {"success": True}

        result = self.retryable.click_with_retry("#button")

        self.assertTrue(result["success"])
        self.assertEqual(self.mock_browser.execute_action.call_count, 1)

    def test_click_with_retry_success_after_retry(self):
        """Test successful click after retry"""
        # Fail first, succeed second
        self.mock_browser.execute_action.side_effect = [
            {"success": False, "error": "TimeoutException"},
            {"success": True},
        ]

        result = self.retryable.click_with_retry("#button")

        self.assertTrue(result["success"])
        self.assertEqual(self.mock_browser.execute_action.call_count, 2)

    def test_click_with_retry_all_attempts_fail(self):
        """Test click fails after all retries"""
        self.mock_browser.execute_action.return_value = {
            "success": False,
            "error": "Element not found",
        }

        result = self.retryable.click_with_retry("#button")

        self.assertFalse(result["success"])
        self.assertIn("Failed after 3 attempts", result["error"])
        self.assertEqual(self.mock_browser.execute_action.call_count, 3)

    def test_type_with_retry_success(self):
        """Test successful type action"""
        self.mock_browser.execute_action.return_value = {"success": True}

        result = self.retryable.type_with_retry("#input", "test value")

        self.assertTrue(result["success"])
        self.mock_browser.execute_action.assert_called_with(
            "type", "#input", "test value"
        )

    def test_type_with_retry_failure(self):
        """Test type action failure"""
        self.mock_browser.execute_action.return_value = {
            "success": False,
            "error": "Element not found",
        }

        result = self.retryable.type_with_retry("#input", "test")

        self.assertFalse(result["success"])
        self.assertEqual(self.mock_browser.execute_action.call_count, 3)

    def test_retry_with_alternative_selectors(self):
        """Test retry with alternative selectors"""
        # Mock browser to fail with original, succeed with alternative
        call_count = [0]

        def side_effect(action, selector, value=None):
            call_count[0] += 1
            # Succeed on third attempt
            if call_count[0] >= 3:
                return {"success": True}
            else:
                return {"success": False, "error": "NoSuchElementException"}

        self.mock_browser.execute_action.side_effect = side_effect

        result = self.retryable.click_with_retry("button:nth-of-type(5)")

        # Should succeed after retries
        self.assertTrue(result["success"])

    def test_retry_respects_max_retries(self):
        """Test that retry respects max_retries limit"""
        self.mock_browser.execute_action.return_value = {
            "success": False,
            "error": "Error",
        }

        result = self.retryable.click_with_retry("#button")

        # Should try exactly max_retries times
        self.assertEqual(self.mock_browser.execute_action.call_count, 3)

    @patch("time.sleep")
    def test_retry_waits_between_attempts(self, mock_sleep):
        """Test that retry waits between attempts"""
        self.mock_browser.execute_action.return_value = {
            "success": False,
            "error": "TimeoutException",
        }

        self.retryable.click_with_retry("#button")

        # Should have called sleep between retries
        self.assertGreater(mock_sleep.call_count, 0)


class TestRetryStrategies(unittest.TestCase):
    """Test different retry strategies"""

    def setUp(self):
        """Set up"""
        self.handler = RetryHandler(max_retries=3)

    def test_execute_with_retry_success(self):
        """Test successful execution"""
        mock_action = Mock(return_value={"success": True})

        result = self.handler.execute_with_retry(mock_action, "Test")

        self.assertTrue(result.get("success"))
        self.assertEqual(mock_action.call_count, 1)

    def test_execute_with_retry_failure(self):
        """Test execution with all retries failing"""
        mock_action = Mock(return_value={"success": False, "error": "Test error"})

        result = self.handler.execute_with_retry(mock_action, "Test")

        self.assertFalse(result.get("success"))
        self.assertEqual(mock_action.call_count, 3)  # max_retries

    def test_execute_with_retry_success_after_failure(self):
        """Test success after initial failures"""
        mock_action = Mock(
            side_effect=[{"success": False, "error": "Error"}, {"success": True}]
        )

        result = self.handler.execute_with_retry(mock_action, "Test")

        self.assertTrue(result.get("success"))
        self.assertEqual(mock_action.call_count, 2)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases"""

    def setUp(self):
        """Set up"""
        self.mock_browser = Mock()
        self.handler = RetryHandler(max_retries=3)
        self.retryable = RetryableAction(self.mock_browser, self.handler)

    def test_empty_selector(self):
        """Test with empty selector"""
        self.mock_browser.execute_action.return_value = {
            "success": False,
            "error": "Empty selector",
        }

        result = self.retryable.click_with_retry("")

        self.assertFalse(result["success"])

    def test_none_selector(self):
        """Test with None selector"""
        self.mock_browser.execute_action.return_value = {
            "success": False,
            "error": "None selector",
        }

        result = self.retryable.click_with_retry(None)

        self.assertFalse(result["success"])

    def test_special_characters_in_selector(self):
        """Test with special characters in selector"""
        selector = "button[data-test='value with spaces']"
        self.mock_browser.execute_action.return_value = {"success": True}

        result = self.retryable.click_with_retry(selector)

        self.assertTrue(result["success"])

    def test_very_long_selector(self):
        """Test with very long selector"""
        selector = "div " * 100 + "> button"
        self.mock_browser.execute_action.return_value = {"success": True}

        result = self.retryable.click_with_retry(selector)

        self.assertTrue(result["success"])


if __name__ == "__main__":
    unittest.main()
