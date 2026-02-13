# API Tester - REST API testing integration
import requests
from typing import Dict, Optional, Any
import json
from colorama import Fore, Style


class APITester:
    """API Testing with requests library"""
    
    def __init__(self, base_url: str = "", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.last_response = None
    
    def get(self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> requests.Response:
        """GET request"""
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
        self.last_response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
        return self.last_response
    
    def post(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None, headers: Optional[Dict] = None) -> requests.Response:
        """POST request"""
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
        self.last_response = self.session.post(url, data=data, json=json_data, headers=headers, timeout=self.timeout)
        return self.last_response
    
    def put(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None, headers: Optional[Dict] = None) -> requests.Response:
        """PUT request"""
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
        self.last_response = self.session.put(url, data=data, json=json_data, headers=headers, timeout=self.timeout)
        return self.last_response
    
    def delete(self, endpoint: str, headers: Optional[Dict] = None) -> requests.Response:
        """DELETE request"""
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
        self.last_response = self.session.delete(url, headers=headers, timeout=self.timeout)
        return self.last_response
    
    def assert_status_code(self, expected: int):
        """Assert response status code"""
        actual = self.last_response.status_code
        assert actual == expected, f"Expected {expected}, got {actual}"
    
    def assert_json_contains(self, key: str, value: Any = None):
        """Assert JSON response contains key (and optionally value)"""
        json_data = self.last_response.json()
        assert key in json_data, f"Key '{key}' not found in response"
        if value is not None:
            assert json_data[key] == value, f"Expected {value}, got {json_data[key]}"
    
    def assert_response_time(self, max_seconds: float):
        """Assert response time is under threshold"""
        elapsed = self.last_response.elapsed.total_seconds()
        assert elapsed < max_seconds, f"Response time {elapsed}s exceeds {max_seconds}s"
    
    def print_response(self):
        """Print response details"""
        if not self.last_response:
            return
        
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}API Response{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        print(f"Status: {self.last_response.status_code} {self.last_response.reason}")
        print(f"Time: {self.last_response.elapsed.total_seconds():.2f}s")
        print(f"URL: {self.last_response.url}")
        
        print(f"\n{Fore.YELLOW}Headers:{Style.RESET_ALL}")
        for key, value in self.last_response.headers.items():
            print(f"  {key}: {value}")
        
        print(f"\n{Fore.YELLOW}Body:{Style.RESET_ALL}")
        try:
            print(json.dumps(self.last_response.json(), indent=2))
        except:
            print(self.last_response.text[:500])
        
        print()
