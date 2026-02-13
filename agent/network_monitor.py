# Network Monitor - Track API calls and performance
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from collections import defaultdict


class NetworkMonitor:
    """
    Network Monitor - Theo dõi network requests và performance
    Sử dụng selenium-wire để intercept requests/responses
    """
    
    def __init__(self, output_dir: str = "reports/network"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.requests_log = []
        self.api_calls = []
        self.performance_metrics = {
            "total_requests": 0,
            "failed_requests": 0,
            "slow_requests": [],  # > 2s
            "api_errors": [],
            "total_data_transferred": 0
        }
        
        self.request_types = defaultdict(int)
        self.status_codes = defaultdict(int)
        self.domains = defaultdict(int)
    
    def start_monitoring(self, driver):
        """
        Bắt đầu monitor network
        Driver phải được khởi tạo với wire=True
        """
        if not hasattr(driver, 'requests'):
            print("⚠️ Warning: Driver not initialized with wire=True. Network monitoring disabled.")
            return False
        
        print("🌐 Network monitoring started")
        self.start_time = datetime.now()
        return True
    
    def capture_requests(self, driver):
        """Capture tất cả requests từ driver"""
        if not hasattr(driver, 'requests'):
            return
        
        for request in driver.requests:
            self._process_request(request)
    
    def _process_request(self, request):
        """Process một request"""
        try:
            # Basic info
            request_data = {
                "url": request.url,
                "method": request.method,
                "timestamp": datetime.now().isoformat()
            }
            
            # Response info
            if request.response:
                response = request.response
                request_data.update({
                    "status_code": response.status_code,
                    "response_time_ms": self._calculate_response_time(request),
                    "size_bytes": len(response.body) if response.body else 0,
                    "content_type": response.headers.get('Content-Type', 'unknown')
                })
                
                # Track metrics
                self.performance_metrics["total_requests"] += 1
                self.status_codes[response.status_code] += 1
                
                if response.status_code >= 400:
                    self.performance_metrics["failed_requests"] += 1
                    self.performance_metrics["api_errors"].append({
                        "url": request.url,
                        "status": response.status_code,
                        "timestamp": request_data["timestamp"]
                    })
                
                # Track slow requests (> 2s)
                response_time = request_data.get("response_time_ms", 0)
                if response_time > 2000:
                    self.performance_metrics["slow_requests"].append({
                        "url": request.url,
                        "time_ms": response_time
                    })
                
                # Track data transferred
                self.performance_metrics["total_data_transferred"] += request_data.get("size_bytes", 0)
            
            # Track request types
            self.request_types[request.method] += 1
            
            # Track domains
            from urllib.parse import urlparse
            domain = urlparse(request.url).netloc
            self.domains[domain] += 1
            
            # Check if API call
            if self._is_api_call(request.url):
                self.api_calls.append(request_data)
            
            self.requests_log.append(request_data)
            
        except Exception as e:
            print(f"  ⚠️ Error processing request: {e}")
    
    def _calculate_response_time(self, request) -> int:
        """Calculate response time in milliseconds"""
        try:
            if hasattr(request, 'response') and request.response:
                # Selenium-wire doesn't provide timing directly
                # This is an approximation
                return 0  # Would need custom timing implementation
        except:
            pass
        return 0
    
    def _is_api_call(self, url: str) -> bool:
        """Check if URL is an API call"""
        api_indicators = ['/api/', '/v1/', '/v2/', '/graphql', '.json', '/rest/']
        return any(indicator in url.lower() for indicator in api_indicators)
    
    def get_api_summary(self) -> Dict:
        """Get summary of API calls"""
        if not self.api_calls:
            return {"total_api_calls": 0}
        
        successful = sum(1 for call in self.api_calls 
                        if call.get("status_code", 0) < 400)
        failed = len(self.api_calls) - successful
        
        return {
            "total_api_calls": len(self.api_calls),
            "successful": successful,
            "failed": failed,
            "success_rate": f"{successful/len(self.api_calls)*100:.1f}%",
            "endpoints": list(set(call["url"] for call in self.api_calls))
        }
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary"""
        return {
            "total_requests": self.performance_metrics["total_requests"],
            "failed_requests": self.performance_metrics["failed_requests"],
            "success_rate": f"{(self.performance_metrics['total_requests'] - self.performance_metrics['failed_requests']) / max(self.performance_metrics['total_requests'], 1) * 100:.1f}%",
            "slow_requests_count": len(self.performance_metrics["slow_requests"]),
            "total_data_mb": self.performance_metrics["total_data_transferred"] / (1024 * 1024),
            "request_types": dict(self.request_types),
            "status_codes": dict(self.status_codes),
            "top_domains": dict(sorted(self.domains.items(), key=lambda x: x[1], reverse=True)[:5])
        }
    
    def get_errors(self) -> List[Dict]:
        """Get all errors"""
        return self.performance_metrics["api_errors"]
    
    def get_slow_requests(self) -> List[Dict]:
        """Get slow requests"""
        return self.performance_metrics["slow_requests"]
    
    def save_report(self, filename: Optional[str] = None):
        """Save network report to JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"network_report_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        report = {
            "summary": {
                "monitoring_duration": str(datetime.now() - self.start_time) if hasattr(self, 'start_time') else "N/A",
                "total_requests": self.performance_metrics["total_requests"],
                "failed_requests": self.performance_metrics["failed_requests"],
                "api_calls": len(self.api_calls)
            },
            "performance": self.get_performance_summary(),
            "api_summary": self.get_api_summary(),
            "errors": self.get_errors(),
            "slow_requests": self.get_slow_requests(),
            "all_requests": self.requests_log[:100]  # Limit to first 100
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Network report saved: {filepath}")
        return filepath
    
    def print_summary(self):
        """Print network summary to console"""
        from colorama import Fore, Style
        
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🌐 NETWORK MONITORING SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        perf = self.get_performance_summary()
        api = self.get_api_summary()
        
        print(f"Total Requests: {perf['total_requests']}")
        print(f"Failed Requests: {perf['failed_requests']}")
        print(f"Success Rate: {perf['success_rate']}")
        print(f"Slow Requests (>2s): {perf['slow_requests_count']}")
        print(f"Data Transferred: {perf['total_data_mb']:.2f} MB")
        
        print(f"\n{Fore.YELLOW}API Calls:{Style.RESET_ALL}")
        print(f"  Total: {api['total_api_calls']}")
        if api['total_api_calls'] > 0:
            print(f"  Successful: {api['successful']}")
            print(f"  Failed: {api['failed']}")
            print(f"  Success Rate: {api['success_rate']}")
        
        print(f"\n{Fore.YELLOW}Request Types:{Style.RESET_ALL}")
        for method, count in perf['request_types'].items():
            print(f"  {method}: {count}")
        
        print(f"\n{Fore.YELLOW}Status Codes:{Style.RESET_ALL}")
        for code, count in sorted(perf['status_codes'].items()):
            color = Fore.GREEN if code < 400 else Fore.RED
            print(f"  {color}{code}: {count}{Style.RESET_ALL}")
        
        if self.get_errors():
            print(f"\n{Fore.RED}Errors:{Style.RESET_ALL}")
            for error in self.get_errors()[:5]:  # Show first 5
                print(f"  {error['status']} - {error['url'][:60]}")
        
        print()
    
    def clear(self):
        """Clear all monitoring data"""
        self.requests_log.clear()
        self.api_calls.clear()
        self.performance_metrics = {
            "total_requests": 0,
            "failed_requests": 0,
            "slow_requests": [],
            "api_errors": [],
            "total_data_transferred": 0
        }
        self.request_types.clear()
        self.status_codes.clear()
        self.domains.clear()
