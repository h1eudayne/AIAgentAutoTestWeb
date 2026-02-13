#!/usr/bin/env python3
"""
Intelligent Web Testing with Cerebras Cloud SDK
Ultra-fast inference with llama-3.3-70b

Usage:
    python test_web_cerebras.py --url https://example.com
    python test_web_cerebras.py --url https://chatbot-site.com --api-key YOUR_KEY
"""

import json
import os
import time
from datetime import datetime

import click
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from agent.cerebras_analyzer import CerebrasAnalyzer

# Load .env file
load_dotenv()


class CerebrasWebTester:
    """Intelligent web testing with Cerebras Cloud SDK"""

    def __init__(self, url, api_key=None, headless=True):
        self.url = url
        self.headless = headless
        self.driver = None
        self.wait = None
        self.analyzer = CerebrasAnalyzer(api_key=api_key)
        self.analysis = None
        self.test_strategy = None
        self.results = []

    def setup_driver(self):
        """Setup Chrome driver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

        click.echo(click.style("✓ Driver setup complete", fg="green"))

    def teardown_driver(self):
        """Close driver"""
        if self.driver:
            if not self.headless:
                time.sleep(2)
            self.driver.quit()

    def analyze_website(self):
        """Analyze website with Cerebras"""
        click.echo("\n" + "=" * 80)
        click.echo(click.style("🚀 CEREBRAS WEBSITE ANALYSIS", fg="cyan", bold=True))
        click.echo("=" * 80)

        # Load page
        self.driver.get(self.url)
        time.sleep(3)

        # Get HTML content
        html_content = self.driver.page_source

        click.echo("🔍 Analyzing website with Cerebras (ultra-fast!)...")

        # Analyze with Cerebras
        self.analysis = self.analyzer.analyze_website(html_content, self.url)

        # Display analysis
        click.echo(
            f"\n✓ Website Type: {click.style(self.analysis['website_type'], fg='yellow', bold=True)}"
        )
        click.echo(f"✓ Description: {self.analysis['description']}")
        click.echo(f"✓ Confidence: {self.analysis['confidence'] * 100:.1f}%")

        if self.analysis.get("key_features"):
            click.echo("\n📋 Key Features:")
            for feature in self.analysis["key_features"]:
                click.echo(f"   • {feature}")

        return self.analysis

    def generate_test_strategy(self):
        """Generate test strategy with Cerebras"""
        click.echo("\n" + "=" * 80)
        click.echo(click.style("🧪 GENERATING TEST STRATEGY", fg="cyan", bold=True))
        click.echo("=" * 80)

        click.echo("🚀 Generating intelligent test cases (ultra-fast!)...")

        self.test_strategy = self.analyzer.generate_test_cases(self.analysis)

        # Display strategy
        test_count = len(self.test_strategy.get("test_cases", []))
        question_count = len(self.test_strategy.get("test_questions", []))

        click.echo(f"\n✓ Generated {test_count} test cases")
        click.echo(f"✓ Generated {question_count} test questions")

        return self.test_strategy

    def run_chatbot_tests(self):
        """Run chatbot-specific tests"""
        click.echo("\n" + "=" * 80)
        click.echo(click.style("💬 CHATBOT TESTING", fg="cyan", bold=True))
        click.echo("=" * 80)

        questions = self.test_strategy.get("test_questions", [])

        if not questions:
            click.echo("⚠️ No chatbot questions generated")
            return

        # Find input and button
        input_selectors = [
            (By.CSS_SELECTOR, "textarea"),
            (By.CSS_SELECTOR, "input[type='text']"),
        ]

        button_selectors = [
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, "button"),
        ]

        input_element = None
        for by, selector in input_selectors:
            try:
                input_element = self.driver.find_element(by, selector)
                if input_element.is_displayed():
                    break
            except:
                continue

        if not input_element:
            click.echo(click.style("✗ Could not find input field", fg="red"))
            return

        # Test each question
        for i, q in enumerate(questions, 1):
            question = q.get("question", "")
            expected_keywords = q.get("expected_keywords", [])

            click.echo(f"\n📝 Test {i}/{len(questions)}")
            click.echo(f"Question: {question}")

            try:
                # Type question
                input_element.clear()
                input_element.send_keys(question)
                time.sleep(0.5)

                # Send (try button or Enter)
                try:
                    for by, selector in button_selectors:
                        buttons = self.driver.find_elements(by, selector)
                        for btn in buttons:
                            if btn.is_displayed():
                                btn.click()
                                break
                        break
                except:
                    input_element.send_keys(Keys.RETURN)

                # Wait for response
                click.echo("⏳ Waiting for response...")
                time.sleep(5)

                # Get response
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                response = page_text.split(question)[-1][:500]

                click.echo(f"Response: {response[:200]}...")

                # Validate with Cerebras
                validation = self.analyzer.validate_response(
                    question, response, expected_keywords
                )

                # Display validation
                if validation["is_valid"]:
                    click.echo(
                        click.style(
                            f"✓ Valid (Score: {validation['score']:.2f})", fg="green"
                        )
                    )
                else:
                    click.echo(
                        click.style(
                            f"✗ Invalid (Score: {validation['score']:.2f})", fg="red"
                        )
                    )

                click.echo(f"Feedback: {validation['feedback']}")

                # Save result
                self.results.append(
                    {
                        "test_id": f"chatbot_{i}",
                        "question": question,
                        "response": response[:200],
                        "validation": validation,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                click.echo(click.style(f"✗ Test failed: {e}", fg="red"))
                self.results.append(
                    {
                        "test_id": f"chatbot_{i}",
                        "question": question,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    def run_general_tests(self):
        """Run general test cases"""
        click.echo("\n" + "=" * 80)
        click.echo(click.style("🧪 GENERAL TESTING", fg="cyan", bold=True))
        click.echo("=" * 80)

        test_cases = self.test_strategy.get("test_cases", [])

        for i, tc in enumerate(test_cases, 1):
            click.echo(f"\n📋 Test {i}/{len(test_cases)}: {tc.get('name', 'Unnamed')}")
            click.echo(f"Priority: {tc.get('priority', 'medium')}")
            click.echo(f"Description: {tc.get('description', '')}")
            click.echo(click.style("⊘ Manual test case (not automated)", fg="yellow"))

    def generate_report(self):
        """Generate final report"""
        click.echo("\n" + "=" * 80)
        click.echo(click.style("📊 TEST REPORT", fg="cyan", bold=True))
        click.echo("=" * 80)

        # Print Cerebras analysis report
        report = self.analyzer.generate_report(self.analysis, self.test_strategy)
        click.echo(report)

        # Print test results
        if self.results:
            click.echo("\n" + "=" * 80)
            click.echo("🧪 TEST RESULTS")
            click.echo("=" * 80)

            passed = sum(
                1
                for r in self.results
                if r.get("validation", {}).get("is_valid", False)
            )
            total = len(self.results)

            click.echo(f"\nTotal Tests: {total}")
            click.echo(
                click.style(f"Passed: {passed}", fg="green" if passed > 0 else "red")
            )
            click.echo(click.style(f"Failed: {total - passed}", fg="red"))

            if total > 0:
                click.echo(f"Pass Rate: {passed/total*100:.1f}%")

        # Save JSON report
        os.makedirs("reports", exist_ok=True)
        report_path = f"reports/cerebras_test_{int(time.time())}.json"

        report_data = {
            "url": self.url,
            "timestamp": datetime.now().isoformat(),
            "ai_provider": "Cerebras Cloud SDK",
            "model": "llama-3.3-70b",
            "analysis": self.analysis,
            "test_strategy": self.test_strategy,
            "results": self.results,
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        click.echo(f"\n📄 Report saved: {report_path}")

    def run(self):
        """Run complete intelligent test"""
        try:
            self.setup_driver()
            self.analyze_website()
            self.generate_test_strategy()

            if self.analysis["website_type"] == "chatbot":
                self.run_chatbot_tests()
            else:
                self.run_general_tests()

            self.generate_report()

        except Exception as e:
            click.echo(click.style(f"\n❌ Test failed: {e}", fg="red"))
            import traceback

            traceback.print_exc()

        finally:
            self.teardown_driver()


@click.command()
@click.option("--url", "-u", required=True, help="URL to test")
@click.option(
    "--api-key", "-k", help="Cerebras API key (or set CEREBRAS_API_KEY env var)"
)
@click.option(
    "--headless/--no-headless",
    default=True,
    help="Run in headless mode (default: True)",
)
def main(url, api_key, headless):
    """
    Intelligent Web Testing with Cerebras Cloud SDK

    Ultra-fast inference with llama-3.3-70b!

    Examples:
        python test_web_cerebras.py --url https://chatbot-site.com
        python test_web_cerebras.py -u https://example.com --no-headless
        python test_web_cerebras.py -u https://site.com -k YOUR_API_KEY
    """

    # Check API key
    if not api_key and not os.environ.get("CEREBRAS_API_KEY"):
        click.echo(
            click.style("❌ Error: Cerebras API key required!", fg="red", bold=True)
        )
        click.echo("\nSet API key using one of these methods:")
        click.echo("  1. Environment variable: export CEREBRAS_API_KEY=your_key")
        click.echo("  2. Command line: --api-key YOUR_KEY")
        click.echo("\nGet your API key at: https://cloud.cerebras.ai/")
        click.echo("Ultra-fast inference with llama-3.3-70b!")
        exit(1)

    # Validate URL
    if not url.startswith("http"):
        url = "https://" + url

    # Print header
    click.echo("\n" + "=" * 80)
    click.echo(
        click.style("🚀 CEREBRAS INTELLIGENT WEB TESTING", fg="green", bold=True)
    )
    click.echo("=" * 80)
    click.echo(f"URL: {url}")
    click.echo(f"Headless: {headless}")
    click.echo(f"AI: Cerebras Cloud SDK (llama-3.3-70b)")
    click.echo("=" * 80)

    # Run test
    tester = CerebrasWebTester(url, api_key, headless)
    tester.run()


if __name__ == "__main__":
    main()
