"""
Unit tests for Network Monitor
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.network_monitor import NetworkMonitor


class TestNetworkMonitor(unittest.TestCase):
    """Test NetworkMonitor class"""

    def setUp(self):
        """Set up test monitor with temp directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.monitor = NetworkMonitor(output_dir=self.temp_dir)

    def tearDown(self):
        """Clean up temp directory"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test monitor initialization"""
        self.assertIsNotNone(self.monitor.requests_log)
        self.assertIsNotNone(self.monitor.api_calls)
        self.assertEqual(self.monitor.performance_metrics["total_requests"], 0)
        self.assertTrue(Path(self.temp_dir).exists())

    def test_start_monitoring_without_wire(self):
        """Test start monitoring with non-wire driver"""
        mock_driver = Mock(spec=[])  # Mock without 'requests' attribute

        result = self.monitor.start_monitoring(mock_driver)

        # Should return False and print warning
        self.assertFalse(result)

    def test_start_monitoring_with_wire(self):
        """Test start monitoring with wire driver"""
        mock_driver = Mock()
        mock_driver.requests = []

        self.monitor.start_monitoring(mock_driver)

        self.assertTrue(hasattr(self.monitor, "start_time"))

    def test_is_api_call(self):
        """Test API call detection"""
        # API URLs
        self.assertTrue(self.monitor._is_api_call("https://example.com/api/users"))
        self.assertTrue(self.monitor._is_api_call("https://example.com/v1/data"))
        self.assertTrue(self.monitor._is_api_call("https://example.com/graphql"))
        self.assertTrue(self.monitor._is_api_call("https://example.com/data.json"))

        # Non-API URLs
        self.assertFalse(self.monitor._is_api_call("https://example.com/"))
        self.assertFalse(self.monitor._is_api_call("https://example.com/about"))

    def test_process_request_with_response(self):
        """Test processing request with response"""
        mock_request = Mock()
        mock_request.url = "https://example.com/api/test"
        mock_request.method = "GET"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.body = b"test response"
        mock_response.headers = {"Content-Type": "application/json"}

        mock_request.response = mock_response

        self.monitor._process_request(mock_request)

        # Check metrics updated
        self.assertEqual(self.monitor.performance_metrics["total_requests"], 1)
        self.assertEqual(len(self.monitor.api_calls), 1)
        self.assertEqual(len(self.monitor.requests_log), 1)

    def test_process_request_with_error(self):
        """Test processing request with error status"""
        mock_request = Mock()
        mock_request.url = "https://example.com/api/test"
        mock_request.method = "GET"

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.body = b"not found"
        mock_response.headers = {"Content-Type": "text/html"}

        mock_request.response = mock_response

        self.monitor._process_request(mock_request)

        # Check error tracked
        self.assertEqual(self.monitor.performance_metrics["failed_requests"], 1)
        self.assertEqual(len(self.monitor.performance_metrics["api_errors"]), 1)

    def test_get_api_summary_empty(self):
        """Test API summary with no calls"""
        summary = self.monitor.get_api_summary()

        self.assertEqual(summary["total_api_calls"], 0)

    def test_get_api_summary_with_calls(self):
        """Test API summary with calls"""
        # Add mock API calls
        self.monitor.api_calls = [
            {"url": "https://api.example.com/users", "status_code": 200},
            {"url": "https://api.example.com/posts", "status_code": 200},
            {"url": "https://api.example.com/error", "status_code": 500},
        ]

        summary = self.monitor.get_api_summary()

        self.assertEqual(summary["total_api_calls"], 3)
        self.assertEqual(summary["successful"], 2)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["success_rate"], "66.7%")

    def test_get_performance_summary(self):
        """Test performance summary"""
        # Add mock data
        self.monitor.performance_metrics["total_requests"] = 10
        self.monitor.performance_metrics["failed_requests"] = 2
        self.monitor.request_types["GET"] = 7
        self.monitor.request_types["POST"] = 3
        self.monitor.status_codes[200] = 8
        self.monitor.status_codes[404] = 2

        summary = self.monitor.get_performance_summary()

        self.assertEqual(summary["total_requests"], 10)
        self.assertEqual(summary["failed_requests"], 2)
        self.assertEqual(summary["success_rate"], "80.0%")
        self.assertIn("GET", summary["request_types"])
        self.assertIn(200, summary["status_codes"])

    def test_save_report(self):
        """Test saving report"""
        # Add some data
        self.monitor.performance_metrics["total_requests"] = 5
        self.monitor.api_calls = [{"url": "test", "status_code": 200}]

        filepath = self.monitor.save_report("test_report.json")

        # Check file created
        self.assertTrue(Path(filepath).exists())

        # Check content
        with open(filepath, "r") as f:
            data = json.load(f)

        self.assertIn("summary", data)
        self.assertIn("performance", data)
        self.assertIn("api_summary", data)

    def test_clear(self):
        """Test clearing monitor data"""
        # Add some data
        self.monitor.requests_log.append({"test": "data"})
        self.monitor.api_calls.append({"test": "api"})
        self.monitor.performance_metrics["total_requests"] = 5

        self.monitor.clear()

        # Check cleared
        self.assertEqual(len(self.monitor.requests_log), 0)
        self.assertEqual(len(self.monitor.api_calls), 0)
        self.assertEqual(self.monitor.performance_metrics["total_requests"], 0)


class TestNetworkMonitorIntegration(unittest.TestCase):
    """Integration tests for NetworkMonitor"""

    def setUp(self):
        """Set up"""
        self.temp_dir = tempfile.mkdtemp()
        self.monitor = NetworkMonitor(output_dir=self.temp_dir)

    def tearDown(self):
        """Clean up"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_full_monitoring_workflow(self):
        """Test complete monitoring workflow"""
        # Create mock driver with requests
        mock_driver = Mock()
        mock_requests = []

        # Add mock requests
        for i in range(5):
            mock_request = Mock()
            mock_request.url = f"https://example.com/page{i}"
            mock_request.method = "GET"

            mock_response = Mock()
            mock_response.status_code = 200 if i < 4 else 404
            mock_response.body = b"response"
            mock_response.headers = {"Content-Type": "text/html"}

            mock_request.response = mock_response
            mock_requests.append(mock_request)

        mock_driver.requests = mock_requests

        # Start monitoring
        self.monitor.start_monitoring(mock_driver)

        # Capture requests
        self.monitor.capture_requests(mock_driver)

        # Check results
        self.assertEqual(self.monitor.performance_metrics["total_requests"], 5)
        self.assertEqual(self.monitor.performance_metrics["failed_requests"], 1)

        # Get summaries
        perf = self.monitor.get_performance_summary()
        self.assertEqual(perf["total_requests"], 5)
        self.assertEqual(perf["success_rate"], "80.0%")

        # Save report
        filepath = self.monitor.save_report()
        self.assertTrue(Path(filepath).exists())


if __name__ == "__main__":
    unittest.main()
