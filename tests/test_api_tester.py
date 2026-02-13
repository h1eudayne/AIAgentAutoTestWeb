"""Unit tests for API Tester"""
import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.api_tester import APITester
import requests


class TestAPITester(unittest.TestCase):
    """Test APITester class"""
    
    def setUp(self):
        """Set up test API tester"""
        self.api = APITester(base_url="https://api.example.com")
    
    def test_initialization(self):
        """Test API tester initialization"""
        self.assertEqual(self.api.base_url, "https://api.example.com")
        self.assertEqual(self.api.timeout, 30)
        self.assertIsNotNone(self.api.session)
    
    @patch('requests.Session.get')
    def test_get_request(self, mock_get):
        """Test GET request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response
        
        response = self.api.get("/users")
        
        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()
    
    @patch('requests.Session.post')
    def test_post_request(self, mock_post):
        """Test POST request"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        response = self.api.post("/users", json_data={"name": "test"})
        
        self.assertEqual(response.status_code, 201)
        mock_post.assert_called_once()
    
    def test_assert_status_code_success(self):
        """Test status code assertion success"""
        mock_response = Mock()
        mock_response.status_code = 200
        self.api.last_response = mock_response
        
        self.api.assert_status_code(200)  # Should not raise
    
    def test_assert_status_code_failure(self):
        """Test status code assertion failure"""
        mock_response = Mock()
        mock_response.status_code = 404
        self.api.last_response = mock_response
        
        with self.assertRaises(AssertionError):
            self.api.assert_status_code(200)


if __name__ == "__main__":
    unittest.main()
