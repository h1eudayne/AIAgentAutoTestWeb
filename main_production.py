#!/usr/bin/env python3
"""
AI Web Testing Agent - PRODUCTION MODE
Full-featured with all advanced capabilities:
- Retry Loop
- State Memory
- Multi-step Planning
- Network Monitoring
- Screenshot Diff
- Coverage Tracking
- Self-healing Selectors
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from colorama import Fore, Style, init

from agent.analyzer import ResultAnalyzer
from agent.coverage_tracker import CoverageTracker

# Import core components
from agent.executor import TestExecutor

# Import advanced features
from agent.network_monitor import NetworkMonitor
from agent.reporter import TestReporter
from agent.screenshot_diff import ScreenshotDiff
from agent.self_healing import SelfHealingSelector
from config.settings import BROWSER_HEADLESS, BROWSER_TIMEOUT, REPORTS_DIR
from tools.browser import BrowserController

init(autoreset=True)


class ProductionWebTestAgent:
    """
    Production-ready AI Web Testing Agent
    với tất cả tính năng advanced
    """

    def __init__(
        self,
        headless: bool = False,
        enable_retry: bool = True,
        enable_memory: bool = True,
        enable_network: bool = True,
        enable_screenshot: bool = True,
        enable_coverage: bool = True,
        enable_healing: bool = True,
    ):

        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🚀 AI Web Testing Agent - PRODUCTION MODE{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

        # Core components
        self.browser = BrowserController(headless=headless, timeout=BROWSER_TIMEOUT)
        self.executor = TestExecutor(
            self.browser, enable_retry=enable_retry, enable_memory=enable_memory
        )
        self.analyzer = ResultAnalyzer()
        self.reporter = TestReporter(REPORTS_DIR)

        # Advanced features
        self.network_monitor = NetworkMonitor() if enable_network else None
        self.screenshot_diff = ScreenshotDiff() if enable_screenshot else None
        self.coverage_tracker = CoverageTracker() if enable_coverage else None
        self.self_healing = (
            SelfHealingSelector(memory=self.executor.memory if enable_memory else None)
            if enable_healing
            else None
        )

        # Print enabled features
        print(f"{Fore.GREEN}✓ Core Features:{Style.RESET_ALL}")
        print(f"  • Retry Loop: {'Enabled' if enable_retry else 'Disabled'}")
        print(f"  • State Memory: {'Enabled' if enable_memory else 'Disabled'}")

        print(f"\n{Fore.GREEN}✓ Advanced Features:{Style.RESET_ALL}")
        print(f"  • Network Monitoring: {'Enabled' if enable_network else 'Disabled'}")
        print(f"  • Screenshot Diff: {'Enabled' if enable_screenshot else 'Disabled'}")
        print(f"  • Coverage Tracking: {'Enabled' if enable_coverage else 'Disabled'}")
        print(
            f"  • Self-healing Selectors: {'Enabled' if enable_healing else 'Disabled'}"
        )

        print(f"\n{Fore.GREEN}✓ Agent initialized successfully{Style.RESET_ALL}\n")

    def test_website(self, url: str, coverage_goals: dict = None):
        """
        Test website với tất cả tính năng

        Args:
            url: Website URL
            coverage_goals: Dict with pages, features, critical_elements
        """
        print(f"{Fore.CYAN}Testing: {url}{Style.RESET_ALL}\n")

        # Set coverage goals
        if self.coverage_tracker and coverage_goals:
            self.coverage_tracker.set_coverage_goals(**coverage_goals)

        # Start network monitoring
        if self.network_monitor:
            try:
                self.network_monitor.start_monitoring(self.browser.driver)
            except ValueError:
                print(
                    f"{Fore.YELLOW}⚠ Network monitoring requires selenium-wire{Style.RESET_ALL}"
                )
                self.network_monitor = None

        # Navigate to page
        print(f"Navigating to {url}...")
        success = self.browser.navigate(url)

        if not success:
            print(f"{Fore.RED}✗ Failed to navigate to {url}{Style.RESET_ALL}")
            return

        # Track page in coverage
        if self.coverage_tracker:
            self.coverage_tracker.track_page(url)

        # Capture baseline screenshot
        if self.screenshot_diff:
            page_name = self._get_page_name(url)
            self.screenshot_diff.capture_baseline(self.browser.driver, page_name)

        # Get page elements
        print("Analyzing page elements...")
        elements = self.browser.get_interactive_elements()
        print(f"Found {len(elements)} interactive elements\n")

        # Generate test cases
        test_cases = self._generate_tests_from_elements(elements, url)
        print(f"Generated {len(test_cases)} test cases\n")

        # Execute tests
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Executing Tests...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"[{i}/{len(test_cases)}] {test_case['name']}")

            # Execute with self-healing if enabled
            if self.self_healing:
                result = self._execute_with_healing(test_case)
            else:
                result = self.executor.execute_test(test_case)

            results.append(result)

            # Track in coverage
            if self.coverage_tracker:
                self.coverage_tracker.track_test_result(
                    test_name=test_case["name"],
                    page=url,
                    elements_tested=[
                        step.get("selector", "") for step in test_case.get("steps", [])
                    ],
                    actions=[
                        step.get("action", "") for step in test_case.get("steps", [])
                    ],
                    success=result["status"] == "passed",
                )

        # Capture network requests
        if self.network_monitor:
            self.network_monitor.capture_requests(self.browser.driver)

        # Capture current screenshot and compare
        if self.screenshot_diff:
            page_name = self._get_page_name(url)
            self.screenshot_diff.capture_current(self.browser.driver, page_name)
            self.screenshot_diff.compare(page_name)

        # Analyze results
        analysis = self.analyzer.analyze(results)

        # Print summaries
        self._print_results_summary(analysis)

        if self.network_monitor:
            self.network_monitor.print_summary()

        if self.screenshot_diff:
            self.screenshot_diff.print_summary()

        if self.coverage_tracker:
            self.coverage_tracker.print_summary()

        if self.self_healing:
            self.self_healing.print_healing_summary()

        # Save reports
        self._save_reports(url, results, analysis)

        return results

    def _generate_tests_from_elements(self, elements: list, url: str) -> list:
        """Generate test cases from elements"""
        test_cases = []

        # Test buttons
        buttons = [
            e
            for e in elements
            if e.get("tag") == "button"
            or (e.get("tag") == "input" and e.get("type") == "submit")
        ]

        for i, btn in enumerate(buttons[:5], 1):
            selector = self._build_selector(btn)
            test_cases.append(
                {
                    "name": f"Test button {i}: {btn.get('text', 'No text')[:30]}",
                    "priority": "high" if i <= 2 else "medium",
                    "steps": [{"action": "click", "selector": selector}],
                }
            )

        # Test inputs
        inputs = [
            e
            for e in elements
            if e.get("tag") == "input"
            and e.get("type") in ["text", "email", "password", "search"]
        ]

        for i, inp in enumerate(inputs[:3], 1):
            selector = self._build_selector(inp)
            test_value = self._get_test_value(inp.get("type", "text"))
            test_cases.append(
                {
                    "name": f"Test input {i}: {inp.get('name', 'unnamed')}",
                    "priority": "medium",
                    "steps": [
                        {"action": "type", "selector": selector, "value": test_value}
                    ],
                }
            )

        # Test links
        links = [e for e in elements if e.get("tag") == "a"][:3]
        for i, link in enumerate(links, 1):
            selector = self._build_selector(link)
            test_cases.append(
                {
                    "name": f"Test link {i}: {link.get('text', 'No text')[:30]}",
                    "priority": "low",
                    "steps": [{"action": "click", "selector": selector}],
                }
            )

        return test_cases

    def _build_selector(self, element: dict) -> str:
        """Build CSS selector from element"""
        if element.get("id"):
            return f"#{element['id']}"
        elif element.get("name"):
            return f"[name='{element['name']}']"
        elif element.get("class"):
            classes = element["class"].split()
            if classes:
                return f".{classes[0]}"

        # Fallback to tag with nth-of-type
        tag = element.get("tag", "div")
        index = element.get("index", 1)
        return f"{tag}:nth-of-type({index})"

    def _get_test_value(self, input_type: str) -> str:
        """Get test value for input type"""
        values = {
            "text": "Test input",
            "email": "test@example.com",
            "password": "TestPass123",
            "search": "search query",
            "tel": "1234567890",
            "url": "https://example.com",
        }
        return values.get(input_type, "test")

    def _execute_with_healing(self, test_case: dict) -> dict:
        """Execute test with self-healing"""
        # Try normal execution first
        result = self.executor.execute_test(test_case)

        # If failed, try healing
        if result["status"] == "failed" and self.self_healing:
            print(f"  {Fore.YELLOW}Attempting self-healing...{Style.RESET_ALL}")

            # Try to heal selectors
            for step in test_case.get("steps", []):
                if "selector" in step:
                    element, healed_selector = self.self_healing.find_element(
                        self.browser.driver,
                        step["selector"],
                        step.get("element_type", "button"),
                    )

                    if healed_selector:
                        step["selector"] = healed_selector

            # Retry with healed selectors
            result = self.executor.execute_test(test_case)

        return result

    def _get_page_name(self, url: str) -> str:
        """Get page name from URL"""
        from urllib.parse import urlparse

        parsed = urlparse(url)
        path = parsed.path.strip("/").replace("/", "_")
        return path if path else "homepage"

    def _print_results_summary(self, analysis: dict):
        """Print test results summary"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 TEST RESULTS SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

        print(f"Total Tests: {analysis['total_tests']}")
        print(f"{Fore.GREEN}✓ Passed: {analysis['passed']}{Style.RESET_ALL}")
        print(f"{Fore.RED}✗ Failed: {analysis['failed']}{Style.RESET_ALL}")
        print(f"Pass Rate: {analysis['pass_rate']}")
        print()

    def _save_reports(self, url: str, results: list, analysis: dict):
        """Save all reports"""
        print(f"{Fore.GREEN}Saving reports...{Style.RESET_ALL}\n")

        # Main test report
        report_path = self.reporter.generate_report(results, analysis)
        print(f"✓ Test report: {report_path}")

        # Network report
        if self.network_monitor:
            network_path = self.network_monitor.save_report()
            print(f"✓ Network report: {network_path}")

        # Screenshot report
        if self.screenshot_diff:
            screenshot_path = self.screenshot_diff.save_report()
            print(f"✓ Screenshot report: {screenshot_path}")

        # Coverage report
        if self.coverage_tracker:
            coverage_path = self.coverage_tracker.save_report()
            print(f"✓ Coverage report: {coverage_path}")

        # Self-healing mappings
        if self.self_healing:
            healing_path = "reports/selector_mappings.json"
            self.self_healing.export_mappings(healing_path)
            print(f"✓ Selector mappings: {healing_path}")

        print()

    def close(self):
        """Close browser and cleanup"""
        self.browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="AI Web Testing Agent - Production Mode"
    )
    parser.add_argument("url", help="Website URL to test")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--no-retry", action="store_true", help="Disable retry logic")
    parser.add_argument("--no-memory", action="store_true", help="Disable state memory")
    parser.add_argument(
        "--no-network", action="store_true", help="Disable network monitoring"
    )
    parser.add_argument(
        "--no-screenshot", action="store_true", help="Disable screenshot diff"
    )
    parser.add_argument(
        "--no-coverage", action="store_true", help="Disable coverage tracking"
    )
    parser.add_argument(
        "--no-healing", action="store_true", help="Disable self-healing"
    )

    args = parser.parse_args()

    # Initialize agent
    agent = ProductionWebTestAgent(
        headless=args.headless,
        enable_retry=not args.no_retry,
        enable_memory=not args.no_memory,
        enable_network=not args.no_network,
        enable_screenshot=not args.no_screenshot,
        enable_coverage=not args.no_coverage,
        enable_healing=not args.no_healing,
    )

    try:
        # Test website
        agent.test_website(args.url)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        import traceback

        traceback.print_exc()
    finally:
        agent.close()


if __name__ == "__main__":
    main()
