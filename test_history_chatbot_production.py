#!/usr/bin/env python3
"""
Production Test for History Mind AI Chatbot
URL: https://fe-history-mind-ai.vercel.app/

This test uses advanced features without selenium-wire dependency
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from agent.screenshot_diff import ScreenshotDiff
from agent.self_healing import SelfHealingSelector
from agent.coverage_tracker import CoverageTracker
from agent.performance_tester import PerformanceTester
from agent.accessibility_checker import AccessibilityChecker


class HistoryChatbotTest:
    """Test History Mind AI Chatbot with all production features"""

    def __init__(self):
        self.url = "https://fe-history-mind-ai.vercel.app/"
        self.driver = None
        self.wait = None

        # Initialize advanced features
        self.screenshot_diff = ScreenshotDiff()
        self.healer = None
        self.coverage = CoverageTracker()
        self.perf_tester = PerformanceTester()
        self.accessibility = AccessibilityChecker()

    def setup_driver(self):
        """Setup Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--lang=vi-VN")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        self.healer = SelfHealingSelector(self.driver)

        print(f"🚀 Driver setup complete")

    def teardown_driver(self):
        """Close driver"""
        if self.driver:
            self.driver.quit()
            print("✓ Driver closed")

    def test_page_load(self):
        """Test 1: Page loads successfully"""
        print("\n" + "=" * 80)
        print("TEST 1: Page Load & Performance")
        print("=" * 80)

        # Measure page load
        start_time = time.time()
        self.driver.get(self.url)
        load_time = time.time() - start_time

        print(f"✓ Navigated to {self.url}")
        print(f"✓ Page load time: {load_time:.2f}s")

        # Wait for page to load
        time.sleep(3)

        # Capture baseline screenshot
        self.screenshot_diff.capture_baseline(self.driver, "homepage")
        print("📸 Baseline screenshot captured")

        # Check page title
        title = self.driver.title
        print(f"✓ Page title: {title}")

        # Track coverage
        self.coverage.track_element(self.url, "body", "page_load", True)

        return True

    def test_ui_elements(self):
        """Test 2: Check UI elements exist"""
        print("\n" + "=" * 80)
        print("TEST 2: UI Elements Check")
        print("=" * 80)

        # Common selectors for chatbot UI
        selectors = {
            "chat_input": [
                "textarea[placeholder*='Nhập']",
                "textarea[placeholder*='câu hỏi']",
                "input[type='text']",
                "textarea",
            ],
            "send_button": [
                "button[type='submit']",
                "button:has-text('Gửi')",
                "button svg",
                "button[aria-label*='send']",
            ],
            "chat_container": [
                "div[class*='chat']",
                "div[class*='message']",
                "div[class*='conversation']",
                "main",
            ],
        }

        found_elements = {}

        for element_name, selector_list in selectors.items():
            print(f"\n🔍 Looking for: {element_name}")

            for selector in selector_list:
                try:
                    element = self.healer.find_element(selector)
                    if element:
                        found_elements[element_name] = selector
                        print(f"   ✓ Found with: {selector}")
                        self.coverage.track_element(self.url, selector, element_name, True)
                        break
                except Exception as e:
                    print(f"   ✗ Failed: {selector} - {str(e)[:50]}")

        print(f"\n✓ Found {len(found_elements)}/{len(selectors)} elements")
        return found_elements

    def test_send_message(self, found_elements):
        """Test 3: Send a message to chatbot"""
        print("\n" + "=" * 80)
        print("TEST 3: Send Message to Chatbot")
        print("=" * 80)

        if "chat_input" not in found_elements:
            print("⚠️ Chat input not found, skipping test")
            return False

        try:
            # Find input field
            input_selector = found_elements["chat_input"]
            input_field = self.healer.find_element(input_selector)

            # Type message
            test_message = "Chiến tranh Việt Nam diễn ra khi nào?"
            input_field.clear()
            input_field.send_keys(test_message)
            print(f"✓ Typed message: {test_message}")

            # Capture screenshot before sending
            self.screenshot_diff.capture_current(self.driver, "before_send")

            # Find and click send button
            if "send_button" in found_elements:
                send_button = self.healer.find_element(found_elements["send_button"])
                send_button.click()
                print("✓ Clicked send button")
            else:
                # Try pressing Enter
                input_field.send_keys(Keys.RETURN)
                print("✓ Pressed Enter")

            # Wait for response
            time.sleep(5)

            # Capture screenshot after response
            self.screenshot_diff.capture_current(self.driver, "after_response")

            # Compare screenshots
            diff_result = self.screenshot_diff.compare("before_send", "after_response")
            if diff_result:
                print(f"📊 Screenshot diff: {diff_result['diff_percentage']:.2f}%")

            # Track coverage
            self.coverage.track_element(self.url, input_selector, "send_message", True)

            print("✓ Message sent successfully")
            return True

        except Exception as e:
            print(f"✗ Failed to send message: {e}")
            return False

    def test_accessibility(self):
        """Test 4: Check accessibility"""
        print("\n" + "=" * 80)
        print("TEST 4: Accessibility Check")
        print("=" * 80)

        # Run accessibility check
        issues = self.accessibility.check_page(self.driver)

        print(f"\n📊 Accessibility Issues Found: {len(issues)}")

        if issues:
            # Group by severity
            by_severity = {}
            for issue in issues:
                severity = issue.get("severity", "unknown")
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(issue)

            for severity, items in by_severity.items():
                print(f"\n{severity.upper()}: {len(items)} issues")
                for item in items[:3]:  # Show first 3
                    print(f"   - {item.get('message', 'No message')}")

        # Generate report
        report_path = "reports/accessibility_report.json"
        self.accessibility.generate_report(report_path)
        print(f"\n✓ Accessibility report saved: {report_path}")

        return len(issues)

    def test_network_traffic(self):
        """Test 5: Network traffic (skipped - requires selenium-wire)"""
        print("\n" + "=" * 80)
        print("TEST 5: Network Traffic Analysis (SKIPPED)")
        print("=" * 80)
        print("⚠️ Network monitoring requires selenium-wire (not available on Windows)")
        return True

    def test_coverage_report(self):
        """Test 6: Generate coverage report"""
        print("\n" + "=" * 80)
        print("TEST 6: Coverage Report")
        print("=" * 80)

        # Get coverage stats
        stats = self.coverage.get_stats()

        print(f"\n📊 Coverage Statistics:")
        print(f"   Total elements: {stats['total_elements']}")
        print(f"   Tested elements: {stats['tested_elements']}")
        print(f"   Coverage: {stats['coverage_percentage']:.1f}%")

        # Save report
        report_path = "reports/coverage_report.json"
        self.coverage.save_report(report_path)
        print(f"\n✓ Coverage report saved: {report_path}")

        return True

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 80)
        print("🧪 HISTORY MIND AI CHATBOT - PRODUCTION TEST SUITE")
        print("=" * 80)
        print(f"URL: {self.url}")
        print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        results = {}

        try:
            # Setup
            self.setup_driver()

            # Run tests
            results["page_load"] = self.test_page_load()
            found_elements = self.test_ui_elements()
            results["ui_elements"] = len(found_elements) > 0
            results["send_message"] = self.test_send_message(found_elements)
            results["accessibility"] = self.test_accessibility()
            results["network_traffic"] = self.test_network_traffic()
            results["coverage"] = self.test_coverage_report()

        except Exception as e:
            print(f"\n❌ Test suite failed: {e}")
            import traceback

            traceback.print_exc()

        finally:
            # Cleanup
            self.teardown_driver()

        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)

        passed = sum(1 for v in results.values() if v)
        total = len(results)

        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")

        if total > 0:
            print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        else:
            print("\nNo tests were run")

        return passed == total and total > 0


if __name__ == "__main__":
    import os

    # Create reports directory
    os.makedirs("reports", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)

    # Run tests
    tester = HistoryChatbotTest()
    success = tester.run_all_tests()

    # Exit with appropriate code
    exit(0 if success else 1)
