#!/usr/bin/env python3
"""
Demo Multi-step Planning
Minh họa cách tạo và thực thi test plans phức tạp
"""

import sys

from colorama import Fore, Style, init

from agent.multi_step_executor import MultiStepExecutor
from agent.multi_step_planner import MultiStepPlanner, StepType, TestPlan, TestStep
from tools.browser import BrowserController

init(autoreset=True)


def demo_templates():
    """Demo 1: Sử dụng templates có sẵn"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}DEMO 1: Test Plan Templates{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    planner = MultiStepPlanner()

    print(f"{Fore.YELLOW}Available templates:{Style.RESET_ALL}")
    templates = planner.list_templates()
    for i, template in enumerate(templates, 1):
        print(f"  {i}. {template}")

    print(
        f"\n{Fore.GREEN}Creating plan from 'login_flow' template...{Style.RESET_ALL}\n"
    )

    plan = planner.create_plan_from_template("login_flow", "plan_001")

    if plan:
        print(planner.visualize_plan(plan))

        # Save plan
        planner.save_plan(plan, "test_plans/login_flow.json")
        print(
            f"{Fore.GREEN}✓ Plan saved to: test_plans/login_flow.json{Style.RESET_ALL}"
        )


def demo_custom_plan():
    """Demo 2: Tạo custom plan"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}DEMO 2: Custom Test Plan{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    planner = MultiStepPlanner()

    print(f"{Fore.GREEN}Creating custom chatbot test plan...{Style.RESET_ALL}\n")

    steps_data = [
        {
            "id": "step1",
            "name": "Navigate to chatbot",
            "type": "navigate",
            "action": "navigate",
            "value": "https://fe-history-mind-ai.vercel.app/",
            "depends_on": [],
        },
        {
            "id": "step2",
            "name": "Wait for page load",
            "type": "wait",
            "action": "wait",
            "value": "2",
            "depends_on": ["step1"],
        },
        {
            "id": "step3",
            "name": "Click Triều đại Trần button",
            "type": "click",
            "action": "click",
            "selector": "button:nth-of-type(2)",
            "depends_on": ["step2"],
        },
        {
            "id": "step4",
            "name": "Wait for response",
            "type": "wait",
            "action": "wait",
            "value": "3",
            "depends_on": ["step3"],
        },
        {
            "id": "step5",
            "name": "Verify response contains 'Trần'",
            "type": "verify",
            "action": "verify",
            "expected": "Trần",
            "depends_on": ["step4"],
        },
        {
            "id": "step6",
            "name": "Click Hai Bà Trưng button",
            "type": "click",
            "action": "click",
            "selector": "button:nth-of-type(3)",
            "depends_on": ["step5"],
        },
        {
            "id": "step7",
            "name": "Wait for response",
            "type": "wait",
            "action": "wait",
            "value": "3",
            "depends_on": ["step6"],
        },
        {
            "id": "step8",
            "name": "Verify response contains 'Hai Bà Trưng'",
            "type": "verify",
            "action": "verify",
            "expected": "Hai Bà Trưng",
            "depends_on": ["step7"],
        },
    ]

    plan = planner.create_custom_plan(
        plan_id="chatbot_001",
        name="Vietnamese History Chatbot Test",
        description="Test chatbot knowledge about Vietnamese history",
        steps_data=steps_data,
    )

    print(planner.visualize_plan(plan))

    # Save plan
    planner.save_plan(plan, "test_plans/chatbot_test.json")
    print(f"{Fore.GREEN}✓ Plan saved to: test_plans/chatbot_test.json{Style.RESET_ALL}")

    return plan


def demo_execution(plan: TestPlan):
    """Demo 3: Thực thi plan"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}DEMO 3: Execute Test Plan{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    print(
        f"{Fore.YELLOW}Do you want to execute this plan? (y/n): {Style.RESET_ALL}",
        end="",
    )
    choice = input().strip().lower()

    if choice != "y":
        print(f"{Fore.YELLOW}Skipping execution{Style.RESET_ALL}")
        return

    print(f"\n{Fore.GREEN}Initializing browser and executor...{Style.RESET_ALL}\n")

    browser = BrowserController(headless=False, timeout=30)
    executor = MultiStepExecutor(browser=browser, enable_retry=True, enable_memory=True)

    try:
        result = executor.execute_plan(
            plan, url="https://fe-history-mind-ai.vercel.app/"
        )

        print(f"\n{Fore.GREEN}✓ Execution completed!{Style.RESET_ALL}")
        print(f"\nResult summary:")
        print(f"  Success rate: {result['success_rate']}")
        print(f"  Duration: {result['duration']:.2f}s")

    except Exception as e:
        print(f"\n{Fore.RED}✗ Execution failed: {e}{Style.RESET_ALL}")
    finally:
        browser.close()


def demo_dependencies():
    """Demo 4: Dependencies và parallel execution"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}DEMO 4: Step Dependencies{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    planner = MultiStepPlanner()

    print(f"{Fore.GREEN}Creating plan with parallel steps...{Style.RESET_ALL}\n")

    steps_data = [
        {
            "id": "step1",
            "name": "Navigate to page",
            "type": "navigate",
            "action": "navigate",
            "value": "https://example.com",
            "depends_on": [],
        },
        {
            "id": "step2a",
            "name": "Fill first name",
            "type": "type",
            "action": "type",
            "selector": "#first-name",
            "value": "John",
            "depends_on": ["step1"],
        },
        {
            "id": "step2b",
            "name": "Fill last name",
            "type": "type",
            "action": "type",
            "selector": "#last-name",
            "value": "Doe",
            "depends_on": ["step1"],
        },
        {
            "id": "step2c",
            "name": "Fill email",
            "type": "type",
            "action": "type",
            "selector": "#email",
            "value": "john@example.com",
            "depends_on": ["step1"],
        },
        {
            "id": "step3",
            "name": "Submit form",
            "type": "click",
            "action": "click",
            "selector": "#submit",
            "depends_on": ["step2a", "step2b", "step2c"],
        },
    ]

    plan = planner.create_custom_plan(
        plan_id="parallel_001",
        name="Parallel Form Filling",
        description="Demonstrates parallel step execution",
        steps_data=steps_data,
    )

    print(planner.visualize_plan(plan))

    print(f"\n{Fore.YELLOW}💡 Note:{Style.RESET_ALL}")
    print("  • Steps 2a, 2b, 2c can execute in parallel (all depend on step1)")
    print("  • Step 3 waits for all three to complete")
    print("  • This optimizes execution time!")


def main():
    print(f"\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}🗺️  MULTI-STEP PLANNING DEMO{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}This demo shows:{Style.RESET_ALL}")
    print("  1. Using pre-built templates")
    print("  2. Creating custom test plans")
    print("  3. Executing plans with dependencies")
    print("  4. Parallel step execution")

    input(f"\n{Fore.GREEN}Press Enter to start...{Style.RESET_ALL}")

    # Demo 1: Templates
    demo_templates()
    input(f"\n{Fore.GREEN}Press Enter for next demo...{Style.RESET_ALL}")

    # Demo 2: Custom plan
    plan = demo_custom_plan()
    input(f"\n{Fore.GREEN}Press Enter for next demo...{Style.RESET_ALL}")

    # Demo 3: Execution
    if plan:
        demo_execution(plan)

    input(f"\n{Fore.GREEN}Press Enter for next demo...{Style.RESET_ALL}")

    # Demo 4: Dependencies
    demo_dependencies()

    # Summary
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}✅ DEMO COMPLETED{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    print(f"{Fore.GREEN}Key Features:{Style.RESET_ALL}")
    print("  ✓ Pre-built templates for common flows")
    print("  ✓ Custom plan creation")
    print("  ✓ Step dependencies management")
    print("  ✓ Parallel execution optimization")
    print("  ✓ Integration with Retry + Memory")

    print(f"\n{Fore.YELLOW}📁 Files created:{Style.RESET_ALL}")
    print("  • test_plans/login_flow.json")
    print("  • test_plans/chatbot_test.json")

    print(f"\n{Fore.CYAN}💡 Next steps:{Style.RESET_ALL}")
    print("  • Create your own test plans")
    print("  • Use templates for common scenarios")
    print("  • Integrate with CI/CD pipelines")
    print()


if __name__ == "__main__":
    # Create test_plans directory
    import os

    os.makedirs("test_plans", exist_ok=True)

    main()
