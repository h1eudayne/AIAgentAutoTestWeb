#!/usr/bin/env python3
"""
AI Web Testing Agent
Sử dụng LLaMA 3 + Selenium để tự động test web
"""

import argparse
import sys
from pathlib import Path

from colorama import Fore, Style, init

from agent.analyzer import ResultAnalyzer
from agent.executor import TestExecutor

# Import agent components
from agent.planner import TestPlanner
from agent.reporter import TestReporter
from config.settings import (
    BROWSER_HEADLESS,
    BROWSER_TIMEOUT,
    LLAMA_MODEL_PATH,
    LLAMA_N_CTX,
    LLAMA_N_GPU_LAYERS,
    REPORTS_DIR,
)
from tools.browser import BrowserController

init(autoreset=True)


class AIWebTestAgent:
    def __init__(self, model_path: str = None, headless: bool = False):
        print(f"{Fore.CYAN}🤖 Initializing AI Web Testing Agent...{Style.RESET_ALL}\n")

        # Initialize components
        model_path = model_path or LLAMA_MODEL_PATH

        if not Path(model_path).exists():
            print(f"{Fore.RED}❌ Model not found at: {model_path}{Style.RESET_ALL}")
            print(
                f"{Fore.YELLOW}💡 Download LLaMA 3 model and update LLAMA_MODEL_PATH{Style.RESET_ALL}"
            )
            print(
                f"{Fore.YELLOW}   Example: https://huggingface.co/TheBloke/Llama-3-8B-GGUF{Style.RESET_ALL}"
            )
            sys.exit(1)

        self.planner = TestPlanner(model_path, LLAMA_N_CTX, LLAMA_N_GPU_LAYERS)
        self.browser = BrowserController(headless=headless, timeout=BROWSER_TIMEOUT)
        self.executor = TestExecutor(self.browser)
        self.analyzer = ResultAnalyzer()
        self.reporter = TestReporter(REPORTS_DIR)

        print(f"{Fore.GREEN}✓ Agent initialized successfully{Style.RESET_ALL}\n")

    def test_website(self, url: str):
        """Main testing workflow"""
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🌐 Testing Website: {url}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

        try:
            # Step 1: Navigate to website
            print(f"{Fore.YELLOW}[1/5] 🚀 Navigating to website...{Style.RESET_ALL}")
            if not self.browser.navigate(url):
                print(f"{Fore.RED}❌ Failed to load website{Style.RESET_ALL}")
                return
            print(f"{Fore.GREEN}✓ Page loaded{Style.RESET_ALL}\n")

            # Step 2: Analyze page
            print(f"{Fore.YELLOW}[2/5] 🔍 Analyzing page structure...{Style.RESET_ALL}")
            page_info = self.browser.get_page_info()
            page_info["dom_structure"] = self.browser.extract_dom_structure()
            page_info["interactive_elements"] = self.browser.get_interactive_elements()

            analysis = self.planner.analyze_page(page_info)
            print(f"{Fore.GREEN}✓ Page analyzed{Style.RESET_ALL}")
            print(f"  Page Type: {analysis.get('page_type', 'unknown')}")
            print(f"  Purpose: {analysis.get('main_purpose', 'N/A')}\n")

            # Step 3: Generate test cases
            print(f"{Fore.YELLOW}[3/5] 🧪 Generating test cases...{Style.RESET_ALL}")
            test_cases = self.planner.generate_test_cases(
                analysis, page_info["interactive_elements"]
            )
            print(
                f"{Fore.GREEN}✓ Generated {len(test_cases)} test cases{Style.RESET_ALL}\n"
            )

            # Step 4: Execute tests
            print(f"{Fore.YELLOW}[4/5] ⚡ Executing tests...{Style.RESET_ALL}")
            results = self.executor.execute_all_tests(test_cases)
            print(f"{Fore.GREEN}✓ Tests completed{Style.RESET_ALL}\n")

            # Step 5: Analyze and report
            print(f"{Fore.YELLOW}[5/5] 📊 Analyzing results...{Style.RESET_ALL}")
            analysis_result = self.analyzer.analyze_results(results)
            analysis_result["page_analysis"] = analysis

            report_file = self.reporter.generate_report(url, results, analysis_result)
            print(f"{Fore.GREEN}✓ Report saved to: {report_file}{Style.RESET_ALL}\n")

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️ Testing interrupted by user{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        print(f"\n{Fore.CYAN}🧹 Cleaning up...{Style.RESET_ALL}")
        self.browser.close()
        print(f"{Fore.GREEN}✓ Done{Style.RESET_ALL}\n")


def main():
    parser = argparse.ArgumentParser(
        description="AI Web Testing Agent - Tự động test web với LLaMA 3 + Selenium"
    )
    parser.add_argument("url", help="URL của website cần test")
    parser.add_argument(
        "--model", help="Đường dẫn đến LLaMA 3 model (.gguf)", default=None
    )
    parser.add_argument(
        "--headless", action="store_true", help="Chạy browser ở chế độ headless"
    )

    args = parser.parse_args()

    # Validate URL
    if not args.url.startswith(("http://", "https://")):
        args.url = "https://" + args.url

    # Run agent
    agent = AIWebTestAgent(model_path=args.model, headless=args.headless)
    agent.test_website(args.url)


if __name__ == "__main__":
    main()
