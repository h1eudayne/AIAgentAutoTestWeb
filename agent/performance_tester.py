# Performance Tester - Load time and performance metrics
from typing import Dict, List
import time
from colorama import Fore, Style


class PerformanceTester:
    """Performance testing and metrics"""
    
    def __init__(self):
        self.metrics = []
    
    def measure_page_load(self, driver, url: str) -> Dict:
        """Measure page load time"""
        start = time.time()
        driver.get(url)
        load_time = time.time() - start
        
        metric = {
            "url": url,
            "load_time": load_time,
            "timestamp": time.time()
        }
        self.metrics.append(metric)
        return metric
    
    def get_average_load_time(self) -> float:
        """Get average load time"""
        if not self.metrics:
            return 0.0
        return sum(m["load_time"] for m in self.metrics) / len(self.metrics)
    
    def print_summary(self):
        """Print performance summary"""
        if not self.metrics:
            return
        
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}⚡ PERFORMANCE SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        print(f"Total Measurements: {len(self.metrics)}")
        print(f"Average Load Time: {self.get_average_load_time():.2f}s")
        print(f"Fastest: {min(m['load_time'] for m in self.metrics):.2f}s")
        print(f"Slowest: {max(m['load_time'] for m in self.metrics):.2f}s")
        print()
