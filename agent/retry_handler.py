# Retry Handler - Intelligent retry mechanism
import time
from typing import Dict, List, Callable
from colorama import Fore, Style

class RetryHandler:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_history = []
    
    def execute_with_retry(self, 
                          action_func: Callable, 
                          action_name: str,
                          *args, 
                          **kwargs) -> Dict:
        """
        Thực thi action với retry thông minh
        Nếu fail, tự động thử các chiến lược khác
        """
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            attempt += 1
            
            try:
                print(f"  {Fore.CYAN}[Attempt {attempt}/{self.max_retries}]{Style.RESET_ALL} {action_name}")
                
                # Execute action
                result = action_func(*args, **kwargs)
                
                # Check if successful
                if result.get("success"):
                    if attempt > 1:
                        print(f"  {Fore.GREEN}✓ Success after {attempt} attempts{Style.RESET_ALL}")
                    
                    self.retry_history.append({
                        "action": action_name,
                        "attempts": attempt,
                        "status": "success"
                    })
                    return result
                
                # Failed but no exception
                last_error = result.get("error", "Unknown error")
                print(f"  {Fore.YELLOW}⚠ Attempt {attempt} failed: {last_error}{Style.RESET_ALL}")
                
                # Analyze error and adjust strategy
                if attempt < self.max_retries:
                    strategy = self._get_retry_strategy(last_error, attempt)
                    print(f"  {Fore.CYAN}💡 Retry strategy: {strategy['description']}{Style.RESET_ALL}")
                    
                    # Apply strategy
                    self._apply_strategy(strategy, kwargs)
                    time.sleep(strategy['wait_time'])
                
            except Exception as e:
                last_error = str(e)
                print(f"  {Fore.RED}✗ Exception in attempt {attempt}: {last_error}{Style.RESET_ALL}")
                
                if attempt < self.max_retries:
                    time.sleep(1 * attempt)  # Exponential backoff
        
        # All retries failed
        print(f"  {Fore.RED}✗ All {self.max_retries} attempts failed{Style.RESET_ALL}")
        self.retry_history.append({
            "action": action_name,
            "attempts": self.max_retries,
            "status": "failed",
            "error": last_error
        })
        
        return {
            "success": False,
            "error": f"Failed after {self.max_retries} attempts: {last_error}"
        }
    
    def _get_retry_strategy(self, error: str, attempt: int) -> Dict:
        """
        Phân tích lỗi và đưa ra chiến lược retry thông minh
        """
        error_lower = str(error).lower()
        
        # Timeout errors
        if "timeout" in error_lower or "timed out" in error_lower:
            return {
                "type": "increase_timeout",
                "description": "Increase wait time",
                "wait_time": 2 * attempt,
                "adjustments": {"timeout": 10 * attempt}
            }
        
        # Element not found
        if "not found" in error_lower or "no such element" in error_lower:
            return {
                "type": "alternative_selector",
                "description": "Try alternative selector strategy",
                "wait_time": 1,
                "adjustments": {"use_xpath": True, "wait_longer": True}
            }
        
        # Stale element
        if "stale" in error_lower:
            return {
                "type": "refresh_element",
                "description": "Refresh page and retry",
                "wait_time": 2,
                "adjustments": {"refresh": True}
            }
        
        # Click intercepted
        if "click" in error_lower and "intercept" in error_lower:
            return {
                "type": "scroll_and_click",
                "description": "Scroll to element before clicking",
                "wait_time": 1,
                "adjustments": {"scroll_first": True}
            }
        
        # Invalid selector
        if "invalid selector" in error_lower or "xpath" in error_lower:
            return {
                "type": "fix_selector",
                "description": "Use CSS selector instead",
                "wait_time": 0.5,
                "adjustments": {"use_css": True}
            }
        
        # Default strategy
        return {
            "type": "wait_and_retry",
            "description": "Wait longer and retry",
            "wait_time": 1.5 * attempt,
            "adjustments": {}
        }
    
    def _apply_strategy(self, strategy: Dict, kwargs: Dict):
        """Áp dụng chiến lược retry vào kwargs"""
        adjustments = strategy.get("adjustments", {})
        
        for key, value in adjustments.items():
            kwargs[key] = value
    
    def get_retry_stats(self) -> Dict:
        """Thống kê retry"""
        total = len(self.retry_history)
        if total == 0:
            return {"total": 0, "success": 0, "failed": 0, "avg_attempts": 0}
        
        success = sum(1 for h in self.retry_history if h["status"] == "success")
        failed = total - success
        avg_attempts = sum(h["attempts"] for h in self.retry_history) / total
        
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": f"{success/total*100:.1f}%",
            "avg_attempts": f"{avg_attempts:.1f}"
        }
    
    def get_failed_actions(self) -> List[Dict]:
        """Lấy danh sách actions thất bại"""
        return [h for h in self.retry_history if h["status"] == "failed"]


class SmartSelector:
    """
    Smart selector generator - tự động tạo alternative selectors
    """
    @staticmethod
    def generate_alternatives(original_selector: str, element_info: Dict = None) -> List[str]:
        """
        Tạo danh sách selectors thay thế
        """
        alternatives = [original_selector]
        
        # If element_info provided, generate more specific selectors
        if element_info:
            elem_id = element_info.get('id')
            elem_name = element_info.get('name')
            elem_class = element_info.get('class')
            elem_tag = element_info.get('tag', 'button')
            elem_text = element_info.get('text', '')
            
            if elem_id:
                alternatives.append(f"#{elem_id}")
                alternatives.append(f"{elem_tag}#{elem_id}")
            
            if elem_name:
                alternatives.append(f"[name='{elem_name}']")
                alternatives.append(f"{elem_tag}[name='{elem_name}']")
            
            if elem_class:
                alternatives.append(f".{elem_class.split()[0]}")
            
            if elem_text:
                # XPath by text
                alternatives.append(f"//{elem_tag}[contains(text(), '{elem_text[:20]}')]")
        
        # Generic alternatives based on selector type
        if original_selector.startswith('#'):
            # ID selector - try attribute selector
            elem_id = original_selector[1:]
            alternatives.append(f"[id='{elem_id}']")
        
        elif original_selector.startswith('.'):
            # Class selector - try attribute selector
            class_name = original_selector[1:]
            alternatives.append(f"[class*='{class_name}']")
        
        elif ':nth-of-type' in original_selector or ':nth-child' in original_selector:
            # Nth selector - try without nth
            base = original_selector.split(':')[0]
            alternatives.append(base)
            alternatives.append(f"{base}:first-of-type")
        
        return alternatives


class RetryableAction:
    """
    Wrapper cho actions có thể retry
    """
    def __init__(self, browser, retry_handler: RetryHandler):
        self.browser = browser
        self.retry_handler = retry_handler
        self.smart_selector = SmartSelector()
    
    def click_with_retry(self, selector: str, element_info: Dict = None) -> Dict:
        """Click với retry thông minh"""
        
        # Handle None or empty selector
        if selector is None:
            selector = ""
        
        def click_action(scroll_first=False, **kwargs):
            if scroll_first:
                try:
                    element = self.browser.driver.find_element("css selector", selector)
                    self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(0.5)
                except:
                    pass
            
            return self.browser.execute_action("click", selector)
        
        # Try original selector first
        selector_display = selector[:50] if selector else "(empty)"
        result = self.retry_handler.execute_with_retry(
            click_action,
            f"Click: {selector_display}"
        )
        
        # If failed, try alternative selectors
        if not result.get("success") and element_info:
            alternatives = self.smart_selector.generate_alternatives(selector, element_info)
            
            for alt_selector in alternatives[1:]:  # Skip first (original)
                print(f"  {Fore.CYAN}🔄 Trying alternative selector: {alt_selector[:50]}{Style.RESET_ALL}")
                
                result = self.retry_handler.execute_with_retry(
                    lambda: self.browser.execute_action("click", alt_selector),
                    f"Click (alt): {alt_selector[:50]}",
                )
                
                if result.get("success"):
                    break
        
        return result
    
    def type_with_retry(self, selector: str, value: str, element_info: Dict = None) -> Dict:
        """Type với retry thông minh"""
        
        # Handle None or empty selector
        if selector is None:
            selector = ""
        
        def type_action(**kwargs):
            return self.browser.execute_action("type", selector, value)
        
        result = self.retry_handler.execute_with_retry(
            type_action,
            f"Type: {selector[:50]}"
        )
        
        # Try alternatives if failed
        if not result.get("success") and element_info:
            alternatives = self.smart_selector.generate_alternatives(selector, element_info)
            
            for alt_selector in alternatives[1:]:
                print(f"  {Fore.CYAN}🔄 Trying alternative selector: {alt_selector[:50]}{Style.RESET_ALL}")
                
                result = self.retry_handler.execute_with_retry(
                    lambda: self.browser.execute_action("type", alt_selector, value),
                    f"Type (alt): {alt_selector[:50]}"
                )
                
                if result.get("success"):
                    break
        
        return result
