"""
Multi-step Plan Executor
Thực thi test plans với dependency management
"""

import time
from typing import Dict, List, Optional, Set

from colorama import Fore, Style

from agent.memory import StateMemory
from agent.multi_step_planner import StepStatus, StepType, TestPlan, TestStep
from agent.retry_handler import RetryableAction, RetryHandler
from tools.browser import BrowserController


class MultiStepExecutor:
    """
    Executor cho multi-step test plans
    Quản lý dependencies và thực thi theo thứ tự đúng
    """

    def __init__(
        self,
        browser: BrowserController,
        enable_retry: bool = True,
        enable_memory: bool = True,
    ):
        self.browser = browser
        self.enable_retry = enable_retry
        self.enable_memory = enable_memory

        if enable_retry:
            self.retry_handler = RetryHandler(max_retries=3)
            self.retryable_action = RetryableAction(browser, self.retry_handler)

        if enable_memory:
            self.memory = StateMemory()

        self.completed_steps: Set[str] = set()
        self.failed_steps: Set[str] = set()
        self.extracted_data: Dict[str, any] = {}  # Store extracted data from steps

    def execute_plan(self, plan: TestPlan, url: Optional[str] = None) -> Dict:
        """
        Thực thi test plan
        Returns: Execution result với statistics
        """
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📋 Executing Multi-Step Plan: {plan.name}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        print(f"Description: {plan.description}")
        print(f"Total steps: {len(plan.steps)}")
        print(f"Priority: {plan.priority}\n")

        start_time = time.time()
        self.completed_steps.clear()
        self.failed_steps.clear()
        self.extracted_data.clear()

        # Execute steps in dependency order
        while not plan.is_complete() and not self._should_stop(plan):
            executable_steps = plan.get_executable_steps(self.completed_steps)

            if not executable_steps:
                # No more executable steps but plan not complete
                # This means there are blocked steps
                print(f"\n{Fore.RED}⚠️ Plan execution blocked!{Style.RESET_ALL}")
                self._print_blocked_steps(plan)
                break

            # Execute all executable steps
            for step in executable_steps:
                self._execute_step(step, plan, url)

                if step.status == StepStatus.SUCCESS:
                    self.completed_steps.add(step.id)
                elif step.status == StepStatus.FAILED:
                    self.failed_steps.add(step.id)
                    # Check if this is a critical step
                    if self._is_critical_step(step, plan):
                        print(
                            f"\n{Fore.RED}❌ Critical step failed, stopping execution{Style.RESET_ALL}"
                        )
                        break

                time.sleep(0.5)  # Small delay between steps

        end_time = time.time()
        duration = end_time - start_time

        # Generate result
        result = self._generate_result(plan, duration)

        # Print summary
        self._print_summary(result)

        # Save to memory if enabled
        if self.enable_memory and self.memory and url:
            self._save_to_memory(plan, result, url)

        return result

    def _execute_step(self, step: TestStep, plan: TestPlan, url: Optional[str] = None):
        """Thực thi một step"""
        step.status = StepStatus.RUNNING

        print(f"\n{Fore.YELLOW}[Step {step.id}] {step.name}{Style.RESET_ALL}")
        print(f"  Type: {step.type.value}")
        if step.selector:
            print(f"  Selector: {step.selector}")
        if step.value:
            print(f"  Value: {step.value}")

        try:
            if step.type == StepType.NAVIGATE:
                result = self._execute_navigate(step)
            elif step.type == StepType.CLICK:
                result = self._execute_click(step, url)
            elif step.type == StepType.TYPE:
                result = self._execute_type(step, url)
            elif step.type == StepType.SELECT:
                result = self._execute_select(step)
            elif step.type == StepType.WAIT:
                result = self._execute_wait(step)
            elif step.type == StepType.VERIFY:
                result = self._execute_verify(step)
            elif step.type == StepType.SCREENSHOT:
                result = self._execute_screenshot(step)
            elif step.type == StepType.EXTRACT:
                result = self._execute_extract(step)
            else:
                result = {"success": False, "error": f"Unknown step type: {step.type}"}

            step.result = result

            if result.get("success"):
                step.status = StepStatus.SUCCESS
                print(f"  {Fore.GREEN}✓ Success{Style.RESET_ALL}")
            else:
                step.status = StepStatus.FAILED
                print(f"  {Fore.RED}✗ Failed: {result.get('error')}{Style.RESET_ALL}")

        except Exception as e:
            step.status = StepStatus.FAILED
            step.result = {"success": False, "error": str(e)}
            print(f"  {Fore.RED}✗ Exception: {e}{Style.RESET_ALL}")

    def _execute_navigate(self, step: TestStep) -> Dict:
        """Execute navigate step"""
        if step.value:
            success = self.browser.navigate(step.value)
            return {"success": success}
        return {"success": False, "error": "No URL provided"}

    def _execute_click(self, step: TestStep, url: Optional[str] = None) -> Dict:
        """Execute click step"""
        if not step.selector:
            return {"success": False, "error": "No selector provided"}

        # Check memory for best selector
        if self.enable_memory and self.memory and url:
            if self.memory.should_avoid_selector(url, "button", step.selector):
                print(f"    ⚠️ Memory: Selector failed before, trying alternatives...")
                best_selectors = self.memory.get_best_selectors(url, "button", limit=3)
                if best_selectors:
                    step.selector = best_selectors[0]
                    print(f"    💡 Using remembered selector")

        if self.enable_retry and self.retryable_action:
            result = self.retryable_action.click_with_retry(step.selector)
        else:
            result = self.browser.execute_action("click", step.selector)

        # Remember result in memory
        if self.enable_memory and self.memory and url:
            if result.get("success"):
                self.memory.remember_successful_selector(url, "button", step.selector)
            else:
                self.memory.remember_failed_selector(
                    url, "button", step.selector, result.get("error", "")
                )

        return result

    def _execute_type(self, step: TestStep, url: Optional[str] = None) -> Dict:
        """Execute type step"""
        if not step.selector or not step.value:
            return {"success": False, "error": "Missing selector or value"}

        if self.enable_retry and self.retryable_action:
            result = self.retryable_action.type_with_retry(step.selector, step.value)
        else:
            result = self.browser.execute_action("type", step.selector, step.value)

        # Remember result in memory
        if self.enable_memory and self.memory and url:
            if result.get("success"):
                self.memory.remember_successful_selector(url, "input", step.selector)
            else:
                self.memory.remember_failed_selector(
                    url, "input", step.selector, result.get("error", "")
                )

        return result

    def _execute_select(self, step: TestStep) -> Dict:
        """Execute select step"""
        if not step.selector or not step.value:
            return {"success": False, "error": "Missing selector or value"}

        return self.browser.execute_action("select", step.selector, step.value)

    def _execute_wait(self, step: TestStep) -> Dict:
        """Execute wait step"""
        wait_time = int(step.value) if step.value else 2
        time.sleep(wait_time)
        return {"success": True}

    def _execute_verify(self, step: TestStep) -> Dict:
        """Execute verify step"""
        if not step.expected:
            return {"success": False, "error": "No expected value provided"}

        try:
            page_source = self.browser.driver.page_source.lower()
            expected = step.expected.lower()

            if expected in page_source:
                return {"success": True, "verified": True}
            else:
                return {
                    "success": False,
                    "error": f"Expected '{step.expected}' not found",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_screenshot(self, step: TestStep) -> Dict:
        """Execute screenshot step"""
        try:
            filename = step.value if step.value else f"screenshot_{step.id}.png"
            self.browser.driver.save_screenshot(filename)
            return {"success": True, "filename": filename}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_extract(self, step: TestStep) -> Dict:
        """Execute extract step - extract data from page"""
        if not step.selector:
            return {"success": False, "error": "No selector provided"}

        try:
            element = self.browser.driver.find_element("css selector", step.selector)
            extracted_value = element.text

            # Store extracted data
            self.extracted_data[step.id] = extracted_value

            return {"success": True, "extracted": extracted_value}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _should_stop(self, plan: TestPlan) -> bool:
        """Kiểm tra có nên dừng execution không"""
        # Stop if too many failures
        if len(self.failed_steps) > len(plan.steps) * 0.5:
            return True
        return False

    def _is_critical_step(self, step: TestStep, plan: TestPlan) -> bool:
        """Kiểm tra step có critical không"""
        # A step is critical if many other steps depend on it
        dependent_count = sum(1 for s in plan.steps if step.id in s.depends_on)
        return dependent_count >= 2

    def _print_blocked_steps(self, plan: TestPlan):
        """Print các steps bị block"""
        blocked = [step for step in plan.steps if step.status == StepStatus.PENDING]

        if blocked:
            print(f"\n{Fore.YELLOW}Blocked steps:{Style.RESET_ALL}")
            for step in blocked:
                missing_deps = [
                    dep for dep in step.depends_on if dep not in self.completed_steps
                ]
                print(f"  • {step.name} - waiting for: {', '.join(missing_deps)}")

    def _generate_result(self, plan: TestPlan, duration: float) -> Dict:
        """Generate execution result"""
        progress = plan.get_progress()

        return {
            "plan_id": plan.id,
            "plan_name": plan.name,
            "duration": duration,
            "total_steps": progress["total"],
            "completed": progress["completed"],
            "failed": progress["failed"],
            "pending": progress["pending"],
            "success_rate": f"{progress['percentage']:.1f}%",
            "completed_steps": list(self.completed_steps),
            "failed_steps": list(self.failed_steps),
            "extracted_data": self.extracted_data,
            "steps": [step.to_dict() for step in plan.steps],
        }

    def _print_summary(self, result: Dict):
        """Print execution summary"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 EXECUTION SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

        print(f"Plan: {result['plan_name']}")
        print(f"Duration: {result['duration']:.2f}s")
        print(f"Total steps: {result['total_steps']}")
        print(f"{Fore.GREEN}✓ Completed: {result['completed']}{Style.RESET_ALL}")
        print(f"{Fore.RED}✗ Failed: {result['failed']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⏳ Pending: {result['pending']}{Style.RESET_ALL}")
        print(f"Success rate: {result['success_rate']}")

        if result["extracted_data"]:
            print(f"\n{Fore.CYAN}📦 Extracted Data:{Style.RESET_ALL}")
            for key, value in result["extracted_data"].items():
                print(f"  {key}: {value}")

        print()

    def _save_to_memory(self, plan: TestPlan, result: Dict, url: str):
        """Save execution to memory"""
        # Create a test case representation
        test_case = {
            "name": plan.name,
            "priority": plan.priority,
            "steps": [step.to_dict() for step in plan.steps],
        }

        # Create result representation
        test_result = {
            "status": "passed" if result["failed"] == 0 else "failed",
            "errors": [f"Step {step_id} failed" for step_id in result["failed_steps"]],
        }

        self.memory.remember_test_result(url, test_case, test_result)
