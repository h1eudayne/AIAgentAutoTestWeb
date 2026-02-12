# Test Executor
from typing import Dict, List
from tools.browser import BrowserController
import time

class TestExecutor:
    def __init__(self, browser: BrowserController):
        self.browser = browser
        self.results = []
    
    def execute_test_case(self, test_case: Dict) -> Dict:
        """Thực thi một test case"""
        print(f"\n🧪 Executing: {test_case.get('name', 'Unnamed test')}")
        
        result = {
            "name": test_case.get("name"),
            "priority": test_case.get("priority"),
            "status": "passed",
            "steps": [],
            "errors": []
        }
        
        steps = test_case.get("steps", [])
        
        for i, step in enumerate(steps, 1):
            action_desc = f"{step.get('action')} {step.get('selector', '')}"
            if len(action_desc) > 60:
                action_desc = action_desc[:57] + "..."
            print(f"  Step {i}: {action_desc}")
            
            step_result = self._execute_step(step)
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
        return result
    
    def _execute_step(self, step: Dict) -> Dict:
        """Thực thi một bước test"""
        action = step.get("action")
        selector = step.get("selector")
        value = step.get("value")
        
        try:
            if action == "wait":
                time.sleep(int(value) if value else 2)
                return {"success": True, "action": "wait"}
            
            elif action in ["click", "type", "select"]:
                return self.browser.execute_action(action, selector, value)
            
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
    
    def execute_all_tests(self, test_cases: List[Dict]) -> List[Dict]:
        """Thực thi tất cả test cases"""
        print(f"\n🚀 Executing {len(test_cases)} test cases...\n")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"[Test {i}/{len(test_cases)}]")
            try:
                self.execute_test_case(test_case)
            except Exception as e:
                print(f"  ✗ Test failed with exception: {e}")
                self.results.append({
                    "name": test_case.get("name"),
                    "priority": test_case.get("priority"),
                    "status": "failed",
                    "steps": [],
                    "errors": [f"Exception: {str(e)}"]
                })
            
            time.sleep(0.5)  # Reduced from 1 second
        
        return self.results
    
    def get_summary(self) -> Dict:
        """Tổng hợp kết quả"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "passed")
        failed = total - passed
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%"
        }
