# Browser automation tools
import time
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class BrowserController:
    def __init__(self, headless: bool = False, timeout: int = 30):
        self.timeout = timeout
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3")

        try:
            # Try with webdriver-manager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"Warning: webdriver-manager failed ({e}), trying direct Chrome...")
            # Fallback: try without service (use Chrome in PATH)
            try:
                self.driver = webdriver.Chrome(options=options)
            except Exception as e2:
                raise Exception(
                    f"Failed to initialize Chrome WebDriver.\n"
                    f"Error 1: {e}\n"
                    f"Error 2: {e2}\n\n"
                    f"Solutions:\n"
                    f"1. Install Chrome browser: https://www.google.com/chrome/\n"
                    f"2. Or install ChromeDriver manually: https://chromedriver.chromium.org/\n"
                    f"3. Make sure Chrome version matches ChromeDriver version"
                )

        self.driver.set_page_load_timeout(timeout)

    def navigate(self, url: str) -> bool:
        try:
            self.driver.get(url)
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Navigation error: {e}")
            return False

    def get_page_info(self) -> Dict:
        return {
            "url": self.driver.current_url,
            "title": self.driver.title,
            "html": self.driver.page_source,
        }

    def extract_dom_structure(self) -> str:
        soup = BeautifulSoup(self.driver.page_source, "lxml")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get simplified structure
        structure = []
        for tag in soup.find_all(
            ["form", "input", "button", "a", "select", "textarea"]
        ):
            info = {
                "tag": tag.name,
                "id": tag.get("id", ""),
                "class": " ".join(tag.get("class", [])),
                "type": tag.get("type", ""),
                "name": tag.get("name", ""),
                "text": tag.get_text(strip=True)[:50],
            }
            structure.append(info)

        return str(structure)

    def get_interactive_elements(self) -> List[Dict]:
        elements = []

        # Find all interactive elements
        for selector in ["input", "button", "a", "select", "textarea"]:
            found = self.driver.find_elements(By.TAG_NAME, selector)
            for elem in found:
                try:
                    if elem.is_displayed():
                        elements.append(
                            {
                                "tag": selector,
                                "id": elem.get_attribute("id"),
                                "name": elem.get_attribute("name"),
                                "type": elem.get_attribute("type"),
                                "text": elem.text[:50],
                            }
                        )
                except:
                    pass

        return elements

    def execute_action(self, action: str, selector: str, value: str = None) -> Dict:
        try:
            # Set shorter timeout for element finding
            element = self.wait_for_element(selector, timeout=5)

            if action == "click":
                element.click()
                result = {"success": True, "action": "clicked"}
            elif action == "type":
                element.clear()
                element.send_keys(value)
                result = {"success": True, "action": "typed", "value": value}
            elif action == "select":
                from selenium.webdriver.support.ui import Select

                Select(element).select_by_visible_text(value)
                result = {"success": True, "action": "selected", "value": value}
            else:
                result = {"success": False, "error": "Unknown action"}

            time.sleep(0.5)  # Reduced from 1 second
            return result

        except Exception as e:
            return {"success": False, "error": str(e)[:100]}

    def wait_for_element(self, selector: str, timeout: int = None):
        timeout = timeout or self.timeout

        # Try CSS selector first
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
        except:
            # Try XPath
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, selector))
            )

    def take_screenshot(self, filename: str):
        self.driver.save_screenshot(filename)

    def close(self):
        self.driver.quit()
