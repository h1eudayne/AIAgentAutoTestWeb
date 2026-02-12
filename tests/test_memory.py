"""
Unit tests for State Memory System
"""

import unittest
import tempfile
import shutil
import os
from pathlib import Path
import sys
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.memory import StateMemory


class TestStateMemory(unittest.TestCase):
    """Test StateMemory class"""
    
    def setUp(self):
        """Set up test memory with temp directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.memory = StateMemory(memory_dir=self.temp_dir)
        self.test_url = "https://example.com/test"
    
    def tearDown(self):
        """Clean up temp directory"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_memory_initialization(self):
        """Test memory initialization"""
        self.assertTrue(os.path.exists(self.temp_dir))
        self.assertIsNotNone(self.memory.selector_memory)
        self.assertIsNotNone(self.memory.test_history)
        self.assertIsNotNone(self.memory.page_patterns)
    
    def test_get_page_hash(self):
        """Test page hash generation"""
        hash1 = self.memory.get_page_hash(self.test_url)
        hash2 = self.memory.get_page_hash(self.test_url)
        hash3 = self.memory.get_page_hash("https://different.com")
        
        # Same URL should give same hash
        self.assertEqual(hash1, hash2)
        
        # Different URL should give different hash
        self.assertNotEqual(hash1, hash3)
        
        # Hash should be 12 characters
        self.assertEqual(len(hash1), 12)
    
    def test_remember_successful_selector(self):
        """Test remembering successful selector"""
        selector = "#submit-btn"
        
        # Remember once
        self.memory.remember_successful_selector(
            self.test_url, "button", selector
        )
        
        page_hash = self.memory.get_page_hash(self.test_url)
        self.assertIn(page_hash, self.memory.selector_memory)
        
        selectors = self.memory.selector_memory[page_hash]["selectors"]["button"]
        self.assertEqual(len(selectors), 1)
        self.assertEqual(selectors[0]["selector"], selector)
        self.assertEqual(selectors[0]["success_count"], 1)
        
        # Remember again - should increment count
        self.memory.remember_successful_selector(
            self.test_url, "button", selector
        )
        
        selectors = self.memory.selector_memory[page_hash]["selectors"]["button"]
        self.assertEqual(len(selectors), 1)
        self.assertEqual(selectors[0]["success_count"], 2)
    
    def test_remember_failed_selector(self):
        """Test remembering failed selector"""
        selector = "button:nth-of-type(99)"
        error = "Element not found"
        
        self.memory.remember_failed_selector(
            self.test_url, "button", selector, error
        )
        
        page_hash = self.memory.get_page_hash(self.test_url)
        failed = self.memory.selector_memory[page_hash]["failed_selectors"]["button"]
        
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0]["selector"], selector)
        self.assertEqual(failed[0]["error"], error)
    
    def test_get_best_selectors(self):
        """Test getting best selectors"""
        # Add multiple selectors with different success counts
        self.memory.remember_successful_selector(self.test_url, "button", "#btn1")
        self.memory.remember_successful_selector(self.test_url, "button", "#btn1")
        self.memory.remember_successful_selector(self.test_url, "button", "#btn1")
        
        self.memory.remember_successful_selector(self.test_url, "button", "#btn2")
        self.memory.remember_successful_selector(self.test_url, "button", "#btn2")
        
        self.memory.remember_successful_selector(self.test_url, "button", "#btn3")
        
        # Get best selectors
        best = self.memory.get_best_selectors(self.test_url, "button", limit=3)
        
        # Should be sorted by success_count
        self.assertEqual(len(best), 3)
        self.assertEqual(best[0], "#btn1")  # 3 successes
        self.assertEqual(best[1], "#btn2")  # 2 successes
        self.assertEqual(best[2], "#btn3")  # 1 success
    
    def test_should_avoid_selector(self):
        """Test checking if selector should be avoided"""
        selector = "bad-selector"
        
        # Not avoided initially
        self.assertFalse(
            self.memory.should_avoid_selector(self.test_url, "button", selector)
        )
        
        # Add 3 failures
        for i in range(3):
            self.memory.remember_failed_selector(
                self.test_url, "button", selector, "Error"
            )
        
        # Should be avoided now
        self.assertTrue(
            self.memory.should_avoid_selector(self.test_url, "button", selector)
        )
    
    def test_remember_test_result(self):
        """Test remembering test result"""
        test_case = {
            "name": "Test login",
            "priority": "high",
            "steps": [{"action": "click"}]
        }
        
        result = {
            "status": "passed",
            "errors": []
        }
        
        self.memory.remember_test_result(self.test_url, test_case, result)
        
        # Check test was added to history
        self.assertEqual(len(self.memory.test_history), 1)
        self.assertEqual(self.memory.test_history[0]["test_name"], "Test login")
        self.assertEqual(self.memory.test_history[0]["status"], "passed")
    
    def test_get_test_statistics(self):
        """Test getting test statistics"""
        # Add some test results
        for i in range(5):
            test_case = {"name": f"Test {i}", "priority": "high"}
            result = {"status": "passed" if i < 4 else "failed"}
            self.memory.remember_test_result(self.test_url, test_case, result)
        
        stats = self.memory.get_test_statistics(self.test_url)
        
        self.assertEqual(stats["total"], 5)
        self.assertEqual(stats["passed"], 4)
        self.assertEqual(stats["failed"], 1)
        self.assertEqual(stats["pass_rate"], "80.0%")
    
    def test_learn_page_pattern(self):
        """Test learning page pattern"""
        page_info = {
            "elements": [
                {"tag": "button", "class": "btn btn-primary"},
                {"tag": "button", "class": "btn btn-secondary"},
                {"tag": "input", "class": "form-control"},
                {"tag": "a", "class": "nav-link"}
            ]
        }
        
        self.memory.learn_page_pattern(self.test_url, page_info)
        
        page_hash = self.memory.get_page_hash(self.test_url)
        pattern = self.memory.page_patterns[page_hash]
        
        self.assertEqual(pattern["element_counts"]["buttons"], 2)
        self.assertEqual(pattern["element_counts"]["inputs"], 1)
        self.assertEqual(pattern["element_counts"]["links"], 1)
        self.assertIn("btn", pattern["common_classes"])
    
    def test_get_similar_pages(self):
        """Test finding similar pages"""
        # Create two similar pages
        page_info1 = {
            "elements": [
                {"tag": "button", "class": "btn"},
                {"tag": "button", "class": "btn"},
                {"tag": "input", "class": "form"},
            ]
        }
        
        page_info2 = {
            "elements": [
                {"tag": "button", "class": "btn"},
                {"tag": "button", "class": "btn"},
                {"tag": "input", "class": "form"},
            ]
        }
        
        url1 = "https://example.com/page1"
        url2 = "https://example.com/page2"
        
        self.memory.learn_page_pattern(url1, page_info1)
        self.memory.learn_page_pattern(url2, page_info2)
        
        # Find similar pages
        similar = self.memory.get_similar_pages(url1, limit=5)
        
        # Should find url2 as similar
        self.assertEqual(len(similar), 1)
        self.assertEqual(similar[0]["url"], url2)
        self.assertGreater(similar[0]["similarity"], 0.5)
    
    def test_get_recommendations(self):
        """Test getting recommendations"""
        # Add some data
        self.memory.remember_successful_selector(self.test_url, "button", "#btn1")
        self.memory.remember_successful_selector(self.test_url, "button", "#btn1")
        
        test_case = {"name": "Test", "priority": "high"}
        result = {"status": "passed"}
        self.memory.remember_test_result(self.test_url, test_case, result)
        
        page_info = {"elements": [{"tag": "button"}]}
        self.memory.learn_page_pattern(self.test_url, page_info)
        
        # Get recommendations
        recommendations = self.memory.get_recommendations(self.test_url)
        
        self.assertIn("best_selectors", recommendations)
        self.assertIn("similar_pages", recommendations)
        self.assertIn("test_stats", recommendations)
        
        # Check best selectors
        self.assertIn("button", recommendations["best_selectors"])
        self.assertEqual(recommendations["best_selectors"]["button"][0], "#btn1")
        
        # Check test stats
        self.assertEqual(recommendations["test_stats"]["total"], 1)
        self.assertEqual(recommendations["test_stats"]["pass_rate"], "100.0%")
    
    def test_save_session(self):
        """Test saving session"""
        # Add some actions
        self.memory.current_session["actions"].append({"action": "click"})
        self.memory.current_session["successful_selectors"]["#btn"] = 2
        
        initial_history_len = len(self.memory.test_history)
        
        self.memory.save_session()
        
        # Session should be added to history
        self.assertEqual(len(self.memory.test_history), initial_history_len + 1)
        
        # Last entry should be session type
        last_entry = self.memory.test_history[-1]
        self.assertEqual(last_entry["type"], "session")
        self.assertEqual(last_entry["total_actions"], 1)
        self.assertEqual(last_entry["successful_selectors"], 1)
    
    def test_get_memory_stats(self):
        """Test getting memory statistics"""
        # Add some data
        self.memory.remember_successful_selector(self.test_url, "button", "#btn")
        
        test_case = {"name": "Test", "priority": "high"}
        result = {"status": "passed"}
        self.memory.remember_test_result(self.test_url, test_case, result)
        
        page_info = {"elements": []}
        self.memory.learn_page_pattern(self.test_url, page_info)
        
        stats = self.memory.get_memory_stats()
        
        self.assertEqual(stats["total_pages_remembered"], 1)
        self.assertEqual(stats["total_tests_in_history"], 1)
        self.assertEqual(stats["total_page_patterns"], 1)
        self.assertGreater(stats["memory_size_kb"], 0)
    
    def test_memory_persistence(self):
        """Test that memory persists to disk"""
        selector = "#test-btn"
        
        # Remember selector
        self.memory.remember_successful_selector(
            self.test_url, "button", selector
        )
        
        # Create new memory instance with same directory
        memory2 = StateMemory(memory_dir=self.temp_dir)
        
        # Should load existing data
        best = memory2.get_best_selectors(self.test_url, "button")
        self.assertEqual(len(best), 1)
        self.assertEqual(best[0], selector)
    
    def test_test_history_limit(self):
        """Test that test history is limited to 1000 entries"""
        # Add 1100 test results
        for i in range(1100):
            test_case = {"name": f"Test {i}", "priority": "high"}
            result = {"status": "passed"}
            self.memory.remember_test_result(self.test_url, test_case, result)
        
        # Should be limited to 1000
        self.assertEqual(len(self.memory.test_history), 1000)


class TestMemoryEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test memory"""
        self.temp_dir = tempfile.mkdtemp()
        self.memory = StateMemory(memory_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_empty_url(self):
        """Test with empty URL"""
        self.memory.remember_successful_selector("", "button", "#btn")
        
        # Should still work
        best = self.memory.get_best_selectors("", "button")
        self.assertEqual(len(best), 1)
    
    def test_special_characters_in_selector(self):
        """Test with special characters in selector"""
        selector = "button[data-test='value with spaces']"
        
        self.memory.remember_successful_selector(
            "https://example.com", "button", selector
        )
        
        best = self.memory.get_best_selectors("https://example.com", "button")
        self.assertEqual(best[0], selector)
    
    def test_unicode_in_url(self):
        """Test with unicode in URL"""
        url = "https://example.com/trang-chủ"
        
        self.memory.remember_successful_selector(url, "button", "#btn")
        
        best = self.memory.get_best_selectors(url, "button")
        self.assertEqual(len(best), 1)
    
    def test_get_best_selectors_no_data(self):
        """Test getting best selectors when no data"""
        best = self.memory.get_best_selectors("https://new-url.com", "button")
        
        self.assertEqual(len(best), 0)
    
    def test_get_test_statistics_no_tests(self):
        """Test getting statistics when no tests"""
        stats = self.memory.get_test_statistics("https://new-url.com")
        
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["pass_rate"], "0%")
    
    def test_corrupted_json_file(self):
        """Test handling corrupted JSON file"""
        # Write corrupted JSON
        selector_file = Path(self.temp_dir) / "selector_memory.json"
        with open(selector_file, 'w') as f:
            f.write("{ corrupted json")
        
        # Should handle gracefully
        memory2 = StateMemory(memory_dir=self.temp_dir)
        self.assertIsNotNone(memory2.selector_memory)


if __name__ == "__main__":
    unittest.main()
