#!/usr/bin/env python3
"""
Simple Test for History Mind AI Chatbot
URL: https://fe-history-mind-ai.vercel.app/
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


class HistoryChatbotSimpleTest:
    """Simple test for History Mind AI Chatbot"""

    def __init__(self):
        self.url = "https://fe-history-mind-ai.vercel.app/"
        self.driver = None
        self.wait = None

    def setup_driver(self):
        """Setup Chrome driver"""
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Comment out to see browser
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--lang=vi-VN")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

        print(f"🚀 Driver setup complete")

    def teardown_driver(self):
        """Close driver"""
        if self.driver:
            time.sleep(2)  # Wait to see result
            self.driver.quit()
            print("✓ Driver closed")

    def test_page_load(self):
        """Test 1: Page loads successfully"""
        print("\n" + "=" * 80)
        print("TEST 1: Page Load")
        print("=" * 80)

        start_time = time.time()
        self.driver.get(self.url)
        load_time = time.time() - start_time

        print(f"✓ Navigated to {self.url}")
        print(f"✓ Page load time: {load_time:.2f}s")

        # Wait for page to load
        time.sleep(3)

        # Check page title
        title = self.driver.title
        print(f"✓ Page title: {title}")

        # Take screenshot
        os.makedirs("screenshots", exist_ok=True)
        self.driver.save_screenshot("screenshots/homepage.png")
        print("📸 Screenshot saved: screenshots/homepage.png")

        return True

    def test_find_elements(self):
        """Test 2: Find UI elements"""
        print("\n" + "=" * 80)
        print("TEST 2: Find UI Elements")
        print("=" * 80)

        found = {}

        # Try to find input field
        input_selectors = [
            (By.CSS_SELECTOR, "textarea"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.XPATH, "//textarea"),
            (By.XPATH, "//input[@type='text']"),
        ]

        for by, selector in input_selectors:
            try:
                element = self.driver.find_element(by, selector)
                if element.is_displayed():
                    found["input"] = (by, selector)
                    print(f"✓ Found input: {selector}")
                    break
            except:
                pass

        # Try to find send button
        button_selectors = [
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, "button"),
            (By.XPATH, "//button[@type='submit']"),
            (By.XPATH, "//button"),
        ]

        for by, selector in button_selectors:
            try:
                elements = self.driver.find_elements(by, selector)
                for element in elements:
                    if element.is_displayed():
                        found["button"] = (by, selector, element)
                        print(f"✓ Found button: {selector}")
                        break
                if "button" in found:
                    break
            except:
                pass

        # Print page source for debugging
        print("\n📄 Page HTML (first 500 chars):")
        print(self.driver.page_source[:500])

        return found

    def test_send_message(self, found_elements):
        """Test 3: Send a message"""
        print("\n" + "=" * 80)
        print("TEST 3: Send Message")
        print("=" * 80)

        if "input" not in found_elements:
            print("⚠️ Input field not found, skipping test")
            return False

        try:
            # Find and type in input
            by, selector = found_elements["input"]
            input_field = self.driver.find_element(by, selector)

            test_message = "Chiến tranh Việt Nam diễn ra khi nào?"
            input_field.clear()
            input_field.send_keys(test_message)
            print(f"✓ Typed message: {test_message}")

            # Take screenshot before sending
            self.driver.save_screenshot("screenshots/before_send.png")
            print("📸 Screenshot: screenshots/before_send.png")

            # Try to send
            if "button" in found_elements:
                _, _, button = found_elements["button"]
                button.click()
                print("✓ Clicked send button")
            else:
                input_field.send_keys(Keys.RETURN)
                print("✓ Pressed Enter")

            # Wait for response
            print("⏳ Waiting for response...")
            time.sleep(8)

            # Take screenshot after response
            self.driver.save_screenshot("screenshots/after_response.png")
            print("📸 Screenshot: screenshots/after_response.png")

            # Check if page changed
            new_source = self.driver.page_source
            if test_message in new_source:
                print("✓ Message appears in page")

            print("✓ Message sent successfully")
            return True

        except Exception as e:
            print(f"✗ Failed to send message: {e}")
            import traceback

            traceback.print_exc()
            return False

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 80)
        print("🧪 HISTORY MIND AI CHATBOT - SIMPLE TEST")
        print("=" * 80)
        print(f"URL: {self.url}")
        print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        results = {}

        try:
            # Setup
            self.setup_driver()

            # Run tests
            results["page_load"] = self.test_page_load()
            found_elements = self.test_find_elements()
            results["find_elements"] = len(found_elements) > 0
            results["send_message"] = self.test_send_message(found_elements)

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
    # Create screenshots directory
    os.makedirs("screenshots", exist_ok=True)

    # Run tests
    tester = HistoryChatbotSimpleTest()
    success = tester.run_all_tests()

    # Exit with appropriate code
    exit(0 if success else 1)
