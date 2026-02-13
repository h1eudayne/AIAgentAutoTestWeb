#!/usr/bin/env python3
"""
Test script để kiểm tra Selenium hoạt động (không cần LLaMA model)
"""

import time

from tools.browser import BrowserController


def test_browser():
    """Test browser automation cơ bản"""
    print("🧪 Testing Browser Automation (without AI model)...\n")

    try:
        # Initialize browser
        print("1. Initializing browser...")
        browser = BrowserController(headless=False, timeout=30)
        print("   ✓ Browser initialized\n")

        # Navigate to test page
        print("2. Navigating to test page...")
        url = "https://www.selenium.dev/selenium/web/web-form.html"
        if browser.navigate(url):
            print(f"   ✓ Loaded: {url}\n")
        else:
            print("   ✗ Failed to load page\n")
            return

        # Get page info
        print("3. Getting page information...")
        page_info = browser.get_page_info()
        print(f"   Title: {page_info['title']}")
        print(f"   URL: {page_info['url']}\n")

        # Extract DOM structure
        print("4. Extracting DOM structure...")
        dom = browser.extract_dom_structure()
        print(f"   ✓ Found {len(dom)} characters of DOM data\n")

        # Get interactive elements
        print("5. Finding interactive elements...")
        elements = browser.get_interactive_elements()
        print(f"   ✓ Found {len(elements)} interactive elements:")
        for i, elem in enumerate(elements[:5], 1):
            print(
                f"      {i}. {elem['tag']} - {elem.get('type', 'N/A')} - {elem.get('text', 'N/A')[:30]}"
            )
        if len(elements) > 5:
            print(f"      ... and {len(elements) - 5} more\n")

        # Test actions
        print("6. Testing form interactions...")

        # Type in text input
        print("   - Typing in text input...")
        result = browser.execute_action(
            "type", "input[name='my-text']", "Hello AI Agent!"
        )
        if result.get("success"):
            print("     ✓ Text input successful")
        else:
            print(f"     ✗ Failed: {result.get('error')}")

        time.sleep(1)

        # Type in password
        print("   - Typing in password field...")
        result = browser.execute_action(
            "type", "input[name='my-password']", "SecurePass123"
        )
        if result.get("success"):
            print("     ✓ Password input successful")
        else:
            print(f"     ✗ Failed: {result.get('error')}")

        time.sleep(1)

        # Click submit button
        print("   - Clicking submit button...")
        result = browser.execute_action("click", "button[type='submit']")
        if result.get("success"):
            print("     ✓ Button click successful")
        else:
            print(f"     ✗ Failed: {result.get('error')}")

        time.sleep(2)

        # Take screenshot
        print("\n7. Taking screenshot...")
        browser.take_screenshot("test_screenshot.png")
        print("   ✓ Screenshot saved: test_screenshot.png\n")

        print("=" * 60)
        print("✅ All browser tests passed!")
        print("=" * 60)
        print("\n💡 Selenium is working correctly!")
        print("   Next step: Download LLaMA 3 model to enable AI features")
        print("   See DOWNLOAD_MODEL.md for instructions\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        print("\n8. Cleaning up...")
        try:
            browser.close()
            print("   ✓ Browser closed\n")
        except:
            print("   (Browser was not initialized)\n")


if __name__ == "__main__":
    test_browser()
