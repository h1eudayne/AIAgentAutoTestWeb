#!/usr/bin/env python3
"""
Dynamic Web Testing CLI Tool
Test any website with customizable test cases

Usage:
    python test_web.py --url https://example.com
    python test_web.py --url https://example.com --headless
    python test_web.py --url https://example.com --test-cases all
    python test_web.py --interactive
"""

import json
import os
import time
from datetime import datetime

import click
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class DynamicWebTester:
    """Dynamic web testing with configurable test cases"""

    def __init__(self, url, headless=True, timeout=20):
        self.url = url
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.wait = None
        self.results = {}
        self.screenshots_dir = "screenshots"
        self.reports_dir = "reports"

    def setup_driver(self):
        """Setup Chrome driver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, self.timeout)

        # Create directories
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

        click.echo(click.style("✓ Driver setup complete", fg="green"))

    def teardown_driver(self):
        """Close driver"""
        if self.driver:
            if not self.headless:
                time.sleep(2)  # Wait to see result
            self.driver.quit()
            click.echo(click.style("✓ Driver closed", fg="green"))

    def test_page_load(self):
        """Test page load"""
        click.echo("\n" + "=" * 80)
        click.echo(click.style("TEST: Page Load", fg="cyan", bold=True))
        click.echo("=" * 80)

        try:
            start_time = time.time()
            self.driver.get(self.url)
            load_time = time.time() - start_time

            click.echo(f"✓ Page loaded in {load_time:.2f}s")

            # Get page info
            title = self.driver.title
            current_url = self.driver.current_url

            click.echo(f"✓ Title: {title}")
            click.echo(f"✓ URL: {current_url}")

            # Take screenshot
            screenshot_path = os.path.join(
                self.screenshots_dir, f"page_load_{int(time.time())}.png"
            )
            self.driver.save_screenshot(screenshot_path)
            click.echo(f"📸 Screenshot: {screenshot_path}")

            self.results["page_load"] = {
                "status": "pass",
                "load_time": load_time,
                "title": title,
                "url": current_url,
                "screenshot": screenshot_path,
            }
            return True

        except Exception as e:
            click.echo(click.style(f"✗ Failed: {e}", fg="red"))
            self.results["page_load"] = {"status": "fail", "error": str(e)}
            return False

    def test_find_elements(self, element_types=None):
        """Test finding common UI elements"""
        click.echo("\n" + "=" * 80)
        click.echo(click.style("TEST: Find UI Elements", fg="cyan", bold=True))
        click.echo("=" * 80)

        if element_types is None:
            element_types = ["input", "button", "link", "form", "image"]

        found_elements = {}
        selectors_map = {
            "input": [
                (By.CSS_SELECTOR, "input"),
                (By.CSS_SELECTOR, "textarea"),
                (By.XPATH, "//input"),
                (By.XPATH, "//textarea"),
            ],
            "button": [
                (By.CSS_SELECTOR, "button"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.XPATH, "//button"),
            ],
            "link": [(By.CSS_SELECTOR, "a"), (By.XPATH, "//a")],
            "form": [(By.CSS_SELECTOR, "form"), (By.XPATH, "//form")],
            "image": [(By.CSS_SELECTOR, "img"), (By.XPATH, "//img")],
        }

        for element_type in element_types:
            if element_type not in selectors_map:
                continue

            click.echo(f"\n🔍 Looking for: {element_type}")
            selectors = selectors_map[element_type]

            for by, selector in selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    visible_elements = [e for e in elements if e.is_displayed()]

                    if visible_elements:
                        found_elements[element_type] = {
                            "count": len(visible_elements),
                            "selector": selector,
                            "by": str(by),
                        }
                        click.echo(
                            f"   ✓ Found {len(visible_elements)} {element_type}(s)"
                        )
                        break
                except Exception as e:
                    continue

            if element_type not in found_elements:
                click.echo(f"   ✗ No {element_type} found")

        self.results["find_elements"] = {
            "status": "pass" if found_elements else "fail",
            "found": found_elements,
        }

        return found_elements

    def test_links(self, max_links=5):
        """Test if links are valid"""
        click.echo("\n" + "=" * 80)
        click.echo(click.style("TEST: Check Links", fg="cyan", bold=True))
        click.echo("=" * 80)

        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            valid_links = []

            for link in links[:max_links]:
                href = link.get_attribute("href")
                text = link.text.strip()

                if href and href.startswith("http"):
                    valid_links.append({"href": href, "text": text})
                    click.echo(f"✓ Link: {text[:50]} -> {href[:60]}")

            self.results["links"] = {
                "status": "pass",
                "total_links": len(links),
                "checked": len(valid_links),
                "valid_links": valid_links,
            }

            return True

        except Exception as e:
            click.echo(click.style(f"✗ Failed: {e}", fg="red"))
            self.results["links"] = {"status": "fail", "error": str(e)}
            return False

    def test_forms(self):
        """Test form elements"""
        click.echo("\n" + "=" * 80)
        click.echo(click.style("TEST: Check Forms", fg="cyan", bold=True))
        click.echo("=" * 80)

        try:
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            click.echo(f"Found {len(forms)} form(s)")

            form_data = []
            for i, form in enumerate(forms[:3]):  # Check first 3 forms
                inputs = form.find_elements(By.TAG_NAME, "input")
                textareas = form.find_elements(By.TAG_NAME, "textarea")
                buttons = form.find_elements(By.TAG_NAME, "button")

                form_info = {
                    "index": i,
                    "inputs": len(inputs),
                    "textareas": len(textareas),
                    "buttons": len(buttons),
                }
                form_data.append(form_info)

                click.echo(
                    f"✓ Form {i+1}: {len(inputs)} inputs, {len(textareas)} textareas, {len(buttons)} buttons"
                )

            self.results["forms"] = {
                "status": "pass",
                "total_forms": len(forms),
                "forms": form_data,
            }

            return True

        except Exception as e:
            click.echo(click.style(f"✗ Failed: {e}", fg="red"))
            self.results["forms"] = {"status": "fail", "error": str(e)}
            return False

    def test_responsive(self):
        """Test responsive design"""
        click.echo("\n" + "=" * 80)
        click.echo(click.style("TEST: Responsive Design", fg="cyan", bold=True))
        click.echo("=" * 80)

        viewports = {
            "mobile": (375, 667),
            "tablet": (768, 1024),
            "desktop": (1920, 1080),
        }

        responsive_results = {}

        for device, (width, height) in viewports.items():
            try:
                self.driver.set_window_size(width, height)
                time.sleep(1)

                screenshot_path = os.path.join(
                    self.screenshots_dir, f"responsive_{device}_{int(time.time())}.png"
                )
                self.driver.save_screenshot(screenshot_path)

                responsive_results[device] = {
                    "status": "pass",
                    "viewport": f"{width}x{height}",
                    "screenshot": screenshot_path,
                }

                click.echo(f"✓ {device.capitalize()}: {width}x{height}")

            except Exception as e:
                click.echo(click.style(f"✗ {device} failed: {e}", fg="red"))
                responsive_results[device] = {"status": "fail", "error": str(e)}

        self.results["responsive"] = responsive_results
        return True

    def test_performance(self):
        """Test performance metrics"""
        click.echo("\n" + "=" * 80)
        click.echo(click.style("TEST: Performance Metrics", fg="cyan", bold=True))
        click.echo("=" * 80)

        try:
            # Get navigation timing
            navigation_timing = self.driver.execute_script(
                "return window.performance.timing"
            )

            if navigation_timing:
                load_time = (
                    navigation_timing["loadEventEnd"]
                    - navigation_timing["navigationStart"]
                ) / 1000
                dom_ready = (
                    navigation_timing["domContentLoadedEventEnd"]
                    - navigation_timing["navigationStart"]
                ) / 1000

                click.echo(f"✓ Page load time: {load_time:.2f}s")
                click.echo(f"✓ DOM ready time: {dom_ready:.2f}s")

                self.results["performance"] = {
                    "status": "pass",
                    "load_time": load_time,
                    "dom_ready": dom_ready,
                }
            else:
                click.echo("⚠️ Performance timing not available")
                self.results["performance"] = {
                    "status": "skip",
                    "message": "Not available",
                }

            return True

        except Exception as e:
            click.echo(click.style(f"✗ Failed: {e}", fg="red"))
            self.results["performance"] = {"status": "fail", "error": str(e)}
            return False

    def generate_report(self):
        """Generate test report"""
        click.echo("\n" + "=" * 80)
        click.echo(click.style("📊 TEST REPORT", fg="cyan", bold=True))
        click.echo("=" * 80)

        # Count results
        total = len(self.results)
        passed = sum(
            1
            for r in self.results.values()
            if isinstance(r, dict) and r.get("status") == "pass"
        )

        # Print summary
        for test_name, result in self.results.items():
            if isinstance(result, dict):
                status = result.get("status", "unknown")
                if status == "pass":
                    click.echo(click.style(f"✓ PASS: {test_name}", fg="green"))
                elif status == "fail":
                    click.echo(click.style(f"✗ FAIL: {test_name}", fg="red"))
                else:
                    click.echo(click.style(f"⊘ SKIP: {test_name}", fg="yellow"))

        click.echo(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

        # Save JSON report
        report_path = os.path.join(
            self.reports_dir, f"test_report_{int(time.time())}.json"
        )

        report_data = {
            "url": self.url,
            "timestamp": datetime.now().isoformat(),
            "summary": {"total": total, "passed": passed, "failed": total - passed},
            "results": self.results,
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        click.echo(f"\n📄 Report saved: {report_path}")

        return passed == total


@click.command()
@click.option(
    "--url",
    "-u",
    help="URL to test (e.g., https://example.com)",
)
@click.option(
    "--headless/--no-headless",
    default=True,
    help="Run browser in headless mode (default: True)",
)
@click.option(
    "--timeout",
    "-t",
    default=20,
    type=int,
    help="Timeout in seconds (default: 20)",
)
@click.option(
    "--test-cases",
    "-tc",
    type=click.Choice(
        ["all", "basic", "elements", "links", "forms", "responsive", "performance"],
        case_sensitive=False,
    ),
    default="all",
    help="Test cases to run (default: all)",
)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Interactive mode - prompt for all options",
)
def main(url, headless, timeout, test_cases, interactive):
    """
    Dynamic Web Testing Tool

    Test any website with customizable test cases.

    Examples:
        python test_web.py --url https://example.com
        python test_web.py -u https://example.com --no-headless
        python test_web.py --interactive
    """

    # Interactive mode
    if interactive or not url:
        click.echo(
            click.style(
                "\n🧪 Web Testing Tool - Interactive Mode", fg="cyan", bold=True
            )
        )
        click.echo("=" * 80 + "\n")

        url = click.prompt("Enter URL to test", type=str)
        headless = click.confirm("Run in headless mode?", default=True)
        timeout = click.prompt("Timeout (seconds)", type=int, default=20)

        test_cases = click.prompt(
            "Test cases",
            type=click.Choice(
                [
                    "all",
                    "basic",
                    "elements",
                    "links",
                    "forms",
                    "responsive",
                    "performance",
                ]
            ),
            default="all",
        )

    # Validate URL
    if not url.startswith("http"):
        url = "https://" + url

    # Print configuration
    click.echo("\n" + "=" * 80)
    click.echo(click.style("🚀 Starting Web Test", fg="green", bold=True))
    click.echo("=" * 80)
    click.echo(f"URL: {url}")
    click.echo(f"Headless: {headless}")
    click.echo(f"Timeout: {timeout}s")
    click.echo(f"Test Cases: {test_cases}")
    click.echo("=" * 80)

    # Create tester
    tester = DynamicWebTester(url, headless, timeout)

    try:
        # Setup
        tester.setup_driver()

        # Run tests based on selection
        if test_cases in ["all", "basic"]:
            tester.test_page_load()

        if test_cases in ["all", "elements"]:
            tester.test_find_elements()

        if test_cases in ["all", "links"]:
            tester.test_links()

        if test_cases in ["all", "forms"]:
            tester.test_forms()

        if test_cases in ["all", "responsive"]:
            tester.test_responsive()

        if test_cases in ["all", "performance"]:
            tester.test_performance()

        # Generate report
        success = tester.generate_report()

        # Exit code
        exit(0 if success else 1)

    except KeyboardInterrupt:
        click.echo(click.style("\n\n⚠️ Test interrupted by user", fg="yellow"))
        exit(1)

    except Exception as e:
        click.echo(click.style(f"\n\n❌ Test failed: {e}", fg="red"))
        import traceback

        traceback.print_exc()
        exit(1)

    finally:
        tester.teardown_driver()


if __name__ == "__main__":
    main()
