#!/usr/bin/env python3
"""
Demo Advanced Features
Demonstrate: Network Monitoring, Screenshot Diff, Coverage Tracking, Self-healing
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from colorama import Fore, Style, init

from agent.coverage_tracker import CoverageTracker
from agent.network_monitor import NetworkMonitor
from agent.screenshot_diff import ScreenshotDiff
from agent.self_healing import SelfHealingSelector
from tools.browser import BrowserController

init(autoreset=True)


def demo_network_monitoring():
    """Demo Network Monitoring"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🌐 DEMO: Network Monitoring{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    print("Note: Network monitoring requires selenium-wire")
    print("Install: pip install selenium-wire\n")

    try:
        from seleniumwire import webdriver

        # Initialize with selenium-wire
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        # Initialize monitor
        monitor = NetworkMonitor()
        monitor.start_monitoring(driver)

        # Navigate and capture requests
        print("Navigating to example.com...")
        driver.get("https://example.com")

        # Capture requests
        monitor.capture_requests(driver)

        # Print summary
        monitor.print_summary()

        # Save report
        monitor.save_report()

        driver.quit()

    except ImportError:
        print(
            f"{Fore.YELLOW}selenium-wire not installed. Skipping demo.{Style.RESET_ALL}"
        )
        print("Install with: pip install selenium-wire")


def demo_screenshot_diff():
    """Demo Screenshot Diff"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📸 DEMO: Screenshot Diff{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    browser = BrowserController(headless=True)
    diff = ScreenshotDiff()

    try:
        # Navigate to page
        print("Navigating to example.com...")
        browser.navigate("https://example.com")

        # Capture baseline
        print("\n1. Capturing baseline screenshot...")
        diff.capture_baseline(browser.driver, "homepage")

        # Capture current (same page)
        print("2. Capturing current screenshot...")
        diff.capture_current(browser.driver, "homepage")

        # Compare
        print("3. Comparing screenshots...")
        result = diff.compare("homepage", threshold=0.1)

        # Print summary
        diff.print_summary()

        # Save report
        diff.save_report()

    finally:
        browser.close()


def demo_coverage_tracking():
    """Demo Coverage Tracking"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📊 DEMO: Coverage Tracking{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    tracker = CoverageTracker()

    # Set coverage goals
    print("Setting coverage goals...")
    tracker.set_coverage_goals(
        pages=["https://example.com", "https://example.com/about"],
        features=["navigation", "search", "login"],
        critical_elements=["#submit", ".search-btn", "#login-form"],
    )

    # Simulate testing
    print("\nSimulating test execution...")

    # Test 1
    tracker.track_test_result(
        test_name="Test homepage",
        page="https://example.com",
        elements_tested=["#submit", ".nav-link"],
        actions=["click", "type"],
        success=True,
    )

    # Test 2
    tracker.track_test_result(
        test_name="Test navigation",
        page="https://example.com",
        elements_tested=[".nav-link", ".menu-btn"],
        actions=["click"],
        success=True,
    )

    # Test 3 - with failure
    tracker.track_test_result(
        test_name="Test search",
        page="https://example.com",
        elements_tested=[".search-btn"],
        actions=["click"],
        success=False,
    )

    # Track features
    tracker.track_feature("navigation")
    tracker.track_feature("search")

    # Print summary
    tracker.print_summary()

    # Save report
    tracker.save_report()


def demo_self_healing():
    """Demo Self-healing Selector"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🔧 DEMO: Self-healing Selector{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    browser = BrowserController(headless=True)
    healer = SelfHealingSelector()

    try:
        # Navigate to page
        print("Navigating to example.com...")
        browser.navigate("https://example.com")

        # Try to find element with broken selector
        print("\n1. Trying broken selector: button:nth-of-type(99)")
        element, healed_selector = healer.find_element(
            browser.driver, "button:nth-of-type(99)", "button"
        )

        if element:
            print(
                f"   {Fore.GREEN}✓ Element found with healed selector!{Style.RESET_ALL}"
            )
        else:
            print(
                f"   {Fore.YELLOW}⚠ No element found (page may not have buttons){Style.RESET_ALL}"
            )

        # Try another broken selector
        print("\n2. Trying broken selector: #nonexistent-id")
        element, healed_selector = healer.find_element(
            browser.driver, "#nonexistent-id", "a"
        )

        if element:
            print(
                f"   {Fore.GREEN}✓ Element found with healed selector!{Style.RESET_ALL}"
            )

        # Print summary
        healer.print_healing_summary()

        # Export mappings
        healer.export_mappings("reports/selector_mappings.json")

    finally:
        browser.close()


def demo_integrated():
    """Demo all features integrated"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🚀 DEMO: Integrated Advanced Features{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    print("This demo shows how all features work together:")
    print("1. Network monitoring tracks API calls")
    print("2. Screenshot diff detects visual changes")
    print("3. Coverage tracking measures test completeness")
    print("4. Self-healing fixes broken selectors")

    browser = BrowserController(headless=True)
    diff = ScreenshotDiff()
    tracker = CoverageTracker()
    healer = SelfHealingSelector()

    try:
        # Set coverage goals
        tracker.set_coverage_goals(
            pages=["https://example.com"], features=["page_load", "visual_check"]
        )

        # Navigate
        print("\nNavigating to example.com...")
        browser.navigate("https://example.com")
        tracker.track_page("https://example.com")

        # Capture baseline
        print("Capturing baseline screenshot...")
        diff.capture_baseline(browser.driver, "integrated_test")

        # Simulate interaction with self-healing
        print("\nTesting element interaction with self-healing...")
        element, healed_selector = healer.find_element(
            browser.driver, "a:first-of-type", "a"
        )

        if element:
            tracker.track_element(
                "https://example.com",
                healed_selector or "a:first-of-type",
                "click",
                True,
            )

        # Capture current screenshot
        print("Capturing current screenshot...")
        diff.capture_current(browser.driver, "integrated_test")

        # Compare
        print("Comparing screenshots...")
        diff.compare("integrated_test")

        # Track feature
        tracker.track_feature("page_load")
        tracker.track_feature("visual_check")

        # Print all summaries
        print(f"\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
        diff.print_summary()
        tracker.print_summary()
        healer.print_healing_summary()

        # Save reports
        print(f"\n{Fore.GREEN}Saving reports...{Style.RESET_ALL}")
        diff.save_report()
        tracker.save_report()

    finally:
        browser.close()


def main():
    """Main demo menu"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🎯 Advanced Features Demo{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    print("Select demo:")
    print("1. Network Monitoring")
    print("2. Screenshot Diff")
    print("3. Coverage Tracking")
    print("4. Self-healing Selector")
    print("5. Integrated Demo (All features)")
    print("0. Exit")

    choice = input("\nEnter choice (0-5): ").strip()

    if choice == "1":
        demo_network_monitoring()
    elif choice == "2":
        demo_screenshot_diff()
    elif choice == "3":
        demo_coverage_tracking()
    elif choice == "4":
        demo_self_healing()
    elif choice == "5":
        demo_integrated()
    elif choice == "0":
        print("Goodbye!")
        return
    else:
        print(f"{Fore.RED}Invalid choice{Style.RESET_ALL}")
        return

    print(f"\n{Fore.GREEN}Demo completed!{Style.RESET_ALL}")
    print(f"Check reports/ directory for generated reports")


if __name__ == "__main__":
    main()
