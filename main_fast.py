#!/usr/bin/env python3
"""
AI Web Testing Agent - FAST MODE (No LLM required)
Sử dụng rule-based testing thay vì LLM
"""

import sys
import argparse
from pathlib import Path
from colorama import Fore, Style, init
from datetime import datetime

# Import components
from agent.executor import TestExecutor
from agent.analyzer import ResultAnalyzer
from agent.reporter import TestReporter
from tools.browser import BrowserController
from config.settings import BROWSER_HEADLESS, BROWSER_TIMEOUT, REPORTS_DIR

init(autoreset=True)

class FastWebTestAgent:
    def __init__(self, headless: bool = False, enable_retry: bool = True):
        print(f"{Fore.CYAN}🤖 Initializing Fast Web Testing Agent (No LLM)...{Style.RESET_ALL}\n")
        
        self.browser = BrowserController(headless=headless, timeout=BROWSER_TIMEOUT)
        self.executor = TestExecutor(self.browser, enable_retry=enable_retry)
        self.analyzer = ResultAnalyzer()
        self.reporter = TestReporter(REPORTS_DIR)
        
        if enable_retry:
            print(f"{Fore.GREEN}✓ Retry logic enabled (max 3 attempts per action){Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}✓ Agent initialized successfully{Style.RESET_ALL}\n")
    
    def generate_tests_from_elements(self, elements: list) -> list:
        """Generate test cases from page elements (rule-based)"""
        test_cases = []
        
        # Test buttons
        buttons = [e for e in elements if e.get('tag') == 'button' or 
                   (e.get('tag') == 'input' and e.get('type') == 'submit')]
        
        for i, btn in enumerate(buttons[:5], 1):
            # Build selector
            if btn.get('id'):
                selector = f"#{btn['id']}"
            elif btn.get('name'):
                selector = f"button[name='{btn['name']}']"
            else:
                selector = f"button:nth-of-type({i})"
            
            btn_text = btn.get('text', 'Button')[:40]
            
            test_cases.append({
                "name": f"Click button: {btn_text}",
                "priority": "high",
                "steps": [
                    {
                        "action": "click",
                        "selector": selector
                    },
                    {
                        "action": "wait",
                        "value": "1"
                    }
                ]
            })
        
        # Test text inputs
        inputs = [e for e in elements if e.get('tag') == 'input' and 
                  e.get('type') in ['text', 'email', 'password', 'search', None]]
        
        for i, inp in enumerate(inputs[:3], 1):
            if inp.get('id'):
                selector = f"#{inp['id']}"
            elif inp.get('name'):
                selector = f"input[name='{inp['name']}']"
            else:
                inp_type = inp.get('type', 'text')
                selector = f"input[type='{inp_type}']:nth-of-type({i})"
            
            # Determine test value based on type
            test_value = "test@example.com" if inp.get('type') == 'email' else "Test Input 123"
            
            test_cases.append({
                "name": f"Test input: {inp.get('type', 'text')} field",
                "priority": "medium",
                "steps": [
                    {
                        "action": "type",
                        "selector": selector,
                        "value": test_value
                    }
                ]
            })
        
        # Test links
        links = [e for e in elements if e.get('tag') == 'a' and e.get('text')]
        if links and len(test_cases) < 8:
            link = links[0]
            link_text = link.get('text', 'Link')[:40]
            
            test_cases.append({
                "name": f"Click link: {link_text}",
                "priority": "low",
                "steps": [
                    {
                        "action": "click",
                        "selector": "a:first-of-type"
                    }
                ]
            })
        
        # Test select dropdowns
        selects = [e for e in elements if e.get('tag') == 'select']
        for i, sel in enumerate(selects[:2], 1):
            if sel.get('id'):
                selector = f"#{sel['id']}"
            elif sel.get('name'):
                selector = f"select[name='{sel['name']}']"
            else:
                selector = f"select:nth-of-type({i})"
            
            test_cases.append({
                "name": f"Test dropdown selection",
                "priority": "medium",
                "steps": [
                    {
                        "action": "click",
                        "selector": selector
                    }
                ]
            })
        
        # If no tests generated, add basic page load test
        if not test_cases:
            test_cases.append({
                "name": "Basic page load verification",
                "priority": "high",
                "steps": [
                    {
                        "action": "wait",
                        "value": "1"
                    }
                ]
            })
        
        return test_cases
    
    def test_website(self, url: str):
        """Main testing workflow"""
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🌐 Testing Website: {url}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        try:
            # Step 1: Navigate
            print(f"{Fore.YELLOW}[1/4] 🚀 Navigating to website...{Style.RESET_ALL}")
            if not self.browser.navigate(url):
                print(f"{Fore.RED}❌ Failed to load website{Style.RESET_ALL}")
                return
            print(f"{Fore.GREEN}✓ Page loaded{Style.RESET_ALL}\n")
            
            # Step 2: Analyze page (rule-based)
            print(f"{Fore.YELLOW}[2/4] 🔍 Analyzing page structure...{Style.RESET_ALL}")
            page_info = self.browser.get_page_info()
            elements = self.browser.get_interactive_elements()
            
            print(f"{Fore.GREEN}✓ Found {len(elements)} interactive elements{Style.RESET_ALL}")
            
            # Show element summary
            buttons = sum(1 for e in elements if e.get('tag') == 'button')
            inputs = sum(1 for e in elements if e.get('tag') == 'input')
            links = sum(1 for e in elements if e.get('tag') == 'a')
            
            print(f"  - {buttons} buttons")
            print(f"  - {inputs} input fields")
            print(f"  - {links} links\n")
            
            # Step 3: Generate tests (rule-based)
            print(f"{Fore.YELLOW}[3/4] 🧪 Generating test cases...{Style.RESET_ALL}")
            test_cases = self.generate_tests_from_elements(elements)
            print(f"{Fore.GREEN}✓ Generated {len(test_cases)} test cases{Style.RESET_ALL}\n")
            
            # Step 4: Execute tests
            print(f"{Fore.YELLOW}[4/4] ⚡ Executing tests...{Style.RESET_ALL}")
            results = self.executor.execute_all_tests(test_cases)
            print(f"{Fore.GREEN}✓ Tests completed{Style.RESET_ALL}\n")
            
            # Analyze and report
            print(f"{Fore.YELLOW}📊 Analyzing results...{Style.RESET_ALL}")
            analysis_result = self.analyzer.analyze_results(results)
            analysis_result["page_analysis"] = {
                "page_type": "interactive",
                "main_purpose": f"Web page with {len(elements)} interactive elements",
                "elements_summary": {
                    "buttons": buttons,
                    "inputs": inputs,
                    "links": links
                }
            }
            
            # Add retry stats if enabled
            if self.executor.enable_retry:
                retry_stats = self.executor.retry_handler.get_retry_stats()
                analysis_result["retry_stats"] = retry_stats
                
                print(f"\n{Fore.CYAN}🔄 RETRY STATISTICS{Style.RESET_ALL}")
                print(f"  Total actions: {retry_stats['total']}")
                print(f"  Success rate: {retry_stats['success_rate']}")
                print(f"  Avg attempts: {retry_stats['avg_attempts']}")
                
                failed_actions = self.executor.retry_handler.get_failed_actions()
                if failed_actions:
                    print(f"  {Fore.RED}Failed after retries: {len(failed_actions)}{Style.RESET_ALL}")
            
            report_file = self.reporter.generate_report(url, results, analysis_result)
            print(f"{Fore.GREEN}✓ Report saved to: {report_file}{Style.RESET_ALL}\n")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️ Testing interrupted by user{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print(f"\n{Fore.CYAN}🧹 Cleaning up...{Style.RESET_ALL}")
        self.browser.close()
        print(f"{Fore.GREEN}✓ Done{Style.RESET_ALL}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Fast Web Testing Agent - Rule-based testing (No LLM required)"
    )
    parser.add_argument(
        "url",
        help="URL của website cần test"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Chạy browser ở chế độ headless"
    )
    parser.add_argument(
        "--no-retry",
        action="store_true",
        help="Disable retry logic"
    )
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith(("http://", "https://")):
        args.url = "https://" + args.url
    
    # Run agent
    agent = FastWebTestAgent(headless=args.headless, enable_retry=not args.no_retry)
    agent.test_website(args.url)

if __name__ == "__main__":
    main()
