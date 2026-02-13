# Test Executor with Retry Logic and Memory
from typing import Dict, List
from tools.browser import BrowserController
from agent.retry_handler import RetryHandler, RetryableAction
from agent.memory import StateMemory
import time


class TestExecutor:
    def __init__(
        self,
        browser: BrowserController,
        enable_retry: bool = True,
        enable_memory: bool = True,
    ):
        self.browser = browser
        self.results = []
        self.enable_retry = enable_retry
        self.enable_memory = enable_memory

        if enable_retry:
            self.retry_handler = RetryHandler(max_retries=3)
            self.retryable_action = RetryableAction(browser, self.retry_handler)
        else:
            self.retry_handler = None
            self.retryable_action = None

        if enable_memory:
            self.memory = StateMemory()
        else:
            self.memory = None

    def execute_test_case(self, test_case: Dict, url: str = None) -> Dict:
        """Thực thi một test case với memory"""
        print(f"\n🧪 Executing: {test_case.get('name', 'Unnamed test')}")

        result = {
            "name": test_case.get("name"),
            "priority": test_case.get("priority"),
            "status": "passed",
            "steps": [],
            "errors": [],
        }

        steps = test_case.get("steps", [])

        for i, step in enumerate(steps, 1):
            action_desc = f"{step.get('action')} {step.get('selector', '')}"
            if len(action_desc) > 60:
                action_desc = action_desc[:57] + "..."
            print(f"  Step {i}: {action_desc}")

            step_result = self._execute_step(step, url)
            result["steps"].append(step_result)

            if not step_result.get("success"):
                result["status"] = "failed"
                result["errors"].append(f"Step {i} failed: {step_result.get('error')}")
                print(f"    ✗ Failed: {step_result.get('error')}")
                break
            else:
                print(f"    ✓ Success")

            # Verify expected result if provided
            if step.get("expected"):
                verification = self._verify_expectation(step.get("expected"))
                if not verification:
                    result["status"] = "failed"
                    result["errors"].append(f"Step {i}: Expected result not met")

        self.results.append(result)

        # Remember test result in memory
        if self.enable_memory and self.memory and url:
            self.memory.remember_test_result(url, test_case, result)

        return result

    def _execute_step(self, step: Dict, url: str = None) -> Dict:
        """Thực thi một bước test với retry logic và memory"""
        action = step.get("action")
        selector = step.get("selector")
        value = step.get("value")

        try:
            if action == "wait":
                time.sleep(int(value) if value else 2)
                return {"success": True, "action": "wait"}

            elif action == "click":
                # Check memory for best selector
                if self.enable_memory and self.memory and url:
                    if self.memory.should_avoid_selector(url, "button", selector):
                        print(
                            f"    ⚠️ Memory: Selector failed before, trying alternatives..."
                        )
                        best_selectors = self.memory.get_best_selectors(
                            url, "button", limit=3
                        )
                        if best_selectors:
                            selector = best_selectors[0]
                            print(f"    💡 Using remembered selector: {selector[:50]}")

                if self.enable_retry and self.retryable_action:
                    result = self.retryable_action.click_with_retry(selector)
                else:
                    result = self.browser.execute_action("click", selector)

                # Remember result in memory
                if self.enable_memory and self.memory and url:
                    if result.get("success"):
                        self.memory.remember_successful_selector(
                            url, "button", selector
                        )
                    else:
                        self.memory.remember_failed_selector(
                            url, "button", selector, result.get("error", "")
                        )

                return result

            elif action == "type":
                if self.enable_retry and self.retryable_action:
                    result = self.retryable_action.type_with_retry(selector, value)
                else:
                    result = self.browser.execute_action("type", selector, value)

                # Remember result in memory
                if self.enable_memory and self.memory and url:
                    if result.get("success"):
                        self.memory.remember_successful_selector(url, "input", selector)
                    else:
                        self.memory.remember_failed_selector(
                            url, "input", selector, result.get("error", "")
                        )

                return result

            elif action == "select":
                return self.browser.execute_action("select", selector, value)

            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _verify_expectation(self, expected: str) -> bool:
        """Kiểm tra kết quả mong đợi"""
        try:
            page_source = self.browser.driver.page_source.lower()
            return expected.lower() in page_source
        except:
            return False

    def execute_all_tests(self, test_cases: List[Dict], url: str = None) -> List[Dict]:
        """Thực thi tất cả test cases với memory"""
        print(f"\n🚀 Executing {len(test_cases)} test cases...\n")

        for i, test_case in enumerate(test_cases, 1):
            print(f"[Test {i}/{len(test_cases)}]")
            try:
                self.execute_test_case(test_case, url)
            except Exception as e:
                print(f"  ✗ Test failed with exception: {e}")
                self.results.append(
                    {
                        "name": test_case.get("name"),
                        "priority": test_case.get("priority"),
                        "status": "failed",
                        "steps": [],
                        "errors": [f"Exception: {str(e)}"],
                    }
                )

            time.sleep(0.5)  # Reduced from 1 second

        # Save memory session
        if self.enable_memory and self.memory:
            self.memory.save_session()

        return self.results

    def get_summary(self) -> Dict:
        """Tổng hợp kết quả bao gồm retry stats và memory stats"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "passed")
        failed = total - passed

        summary = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
        }

        # Add retry stats if enabled
        if self.enable_retry and self.retry_handler:
            summary["retry_stats"] = self.retry_handler.get_retry_stats()

        # Add memory stats if enabled
        if self.enable_memory and self.memory:
            summary["memory_stats"] = self.memory.get_memory_stats()

        return summary
