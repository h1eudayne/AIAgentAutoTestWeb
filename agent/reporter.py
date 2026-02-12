# Test Reporter
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from colorama import Fore, Style, init

init(autoreset=True)

class TestReporter:
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_report(self, url: str, results: List[Dict], analysis: Dict) -> str:
        """Tạo báo cáo test"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"test_report_{timestamp}.json"
        
        report = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "analysis": analysis
        }
        
        # Save JSON report
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print console report
        self._print_console_report(url, results, analysis)
        
        return str(report_file)
    
    def _print_console_report(self, url: str, results: List[Dict], analysis: Dict):
        """In báo cáo ra console"""
        print("\n" + "="*80)
        print(f"{Fore.CYAN}🤖 AI WEB TESTING AGENT - TEST REPORT{Style.RESET_ALL}")
        print("="*80)
        
        print(f"\n{Fore.YELLOW}📍 URL:{Style.RESET_ALL} {url}")
        print(f"{Fore.YELLOW}⏰ Time:{Style.RESET_ALL} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Summary
        summary = analysis.get("summary", {})
        print(f"\n{Fore.CYAN}📊 SUMMARY{Style.RESET_ALL}")
        print(f"  Total Tests: {summary.get('total_tests', 0)}")
        print(f"  {Fore.GREEN}✓ Passed: {summary.get('passed', 0)}{Style.RESET_ALL}")
        print(f"  {Fore.RED}✗ Failed: {summary.get('failed', 0)}{Style.RESET_ALL}")
        print(f"  Pass Rate: {summary.get('pass_rate', '0%')}")
        
        # Test Results
        print(f"\n{Fore.CYAN}📋 TEST RESULTS{Style.RESET_ALL}")
        for i, result in enumerate(results, 1):
            status = result.get("status", "unknown")
            name = result.get("name", "Unnamed")
            priority = result.get("priority", "medium")
            
            if status == "passed":
                icon = f"{Fore.GREEN}✓{Style.RESET_ALL}"
            else:
                icon = f"{Fore.RED}✗{Style.RESET_ALL}"
            
            print(f"  {icon} [{priority.upper()}] {name}")
            
            if status == "failed":
                for error in result.get("errors", []):
                    print(f"      {Fore.RED}→ {error}{Style.RESET_ALL}")
        
        # Failures Detail
        failures = analysis.get("failures", [])
        if failures:
            print(f"\n{Fore.RED}❌ FAILURES DETAIL{Style.RESET_ALL}")
            for failure in failures:
                print(f"  • {failure.get('test_name')}")
                print(f"    Priority: {failure.get('priority')}")
                failed_step = failure.get("failed_step", {})
                if failed_step:
                    print(f"    Failed at step {failed_step.get('step_number')}: {failed_step.get('error')}")
        
        # Recommendations
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            print(f"\n{Fore.YELLOW}💡 RECOMMENDATIONS{Style.RESET_ALL}")
            for rec in recommendations:
                print(f"  {rec}")
        
        print("\n" + "="*80 + "\n")
