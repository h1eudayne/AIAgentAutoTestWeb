# Self-healing Selector - Tự động sửa selectors khi DOM thay đổi
from typing import Dict, List, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import difflib
from collections import defaultdict


class SelfHealingSelector:
    """
    Self-healing Selector - Tự động tìm và sửa selectors khi DOM thay đổi
    Sử dụng multiple strategies để tìm element khi selector cũ fail
    """

    def __init__(self, memory=None):
        self.memory = memory
        self.healing_history = []
        self.selector_mappings = {}  # old_selector -> new_selector
        self.healing_strategies = [
            self._heal_by_id,
            self._heal_by_text,
            self._heal_by_attributes,
            self._heal_by_position,
            self._heal_by_similarity,
            self._heal_by_parent_context,
        ]

    def find_element(
        self, driver, selector: str, element_type: str = "button"
    ) -> Tuple[Optional[object], Optional[str]]:
        """
        Find element with self-healing

        Returns:
            (element, healed_selector) or (None, None)
        """
        # Try original selector first
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            return element, selector
        except NoSuchElementException:
            pass

        # Check if we have a known mapping
        if selector in self.selector_mappings:
            healed_selector = self.selector_mappings[selector]
            try:
                element = driver.find_element(By.CSS_SELECTOR, healed_selector)
                print(f"  🔧 Using known healed selector: {healed_selector}")
                return element, healed_selector
            except NoSuchElementException:
                pass

        # Try healing strategies
        print(f"  🔧 Self-healing: Original selector failed, trying alternatives...")

        for strategy in self.healing_strategies:
            result = strategy(driver, selector, element_type)
            if result:
                element, healed_selector = result

                # Save mapping
                self.selector_mappings[selector] = healed_selector

                # Record healing
                self._record_healing(selector, healed_selector, strategy.__name__)

                print(f"  ✓ Healed selector found: {healed_selector}")
                return element, healed_selector

        print(f"  ✗ Self-healing failed: No alternative found")
        return None, None

    def _heal_by_id(self, driver, selector: str, element_type: str) -> Optional[Tuple]:
        """Strategy 1: Try to find by ID"""
        try:
            # Extract ID from selector if present
            if "#" in selector:
                element_id = (
                    selector.split("#")[1].split(".")[0].split("[")[0].split(":")[0]
                )
                element = driver.find_element(By.ID, element_id)
                return element, f"#{element_id}"
        except:
            pass
        return None

    def _heal_by_text(
        self, driver, selector: str, element_type: str
    ) -> Optional[Tuple]:
        """Strategy 2: Find by text content"""
        try:
            # Get all elements of the same type
            elements = driver.find_elements(By.TAG_NAME, element_type)

            # Try to match by text
            for element in elements:
                text = element.text.strip().lower()
                if text and len(text) > 2:
                    # Create XPath selector
                    xpath = f"//{element_type}[contains(text(), '{text[:20]}')]"
                    try:
                        found = driver.find_element(By.XPATH, xpath)
                        return found, xpath
                    except:
                        continue
        except:
            pass
        return None

    def _heal_by_attributes(
        self, driver, selector: str, element_type: str
    ) -> Optional[Tuple]:
        """Strategy 3: Find by common attributes"""
        try:
            # Common attributes to check
            attributes = [
                "data-testid",
                "data-test",
                "name",
                "aria-label",
                "title",
                "type",
            ]

            # Get all elements
            elements = driver.find_elements(By.TAG_NAME, element_type)

            for element in elements:
                for attr in attributes:
                    value = element.get_attribute(attr)
                    if value:
                        # Try this attribute selector
                        attr_selector = f"{element_type}[{attr}='{value}']"
                        try:
                            found = driver.find_element(By.CSS_SELECTOR, attr_selector)
                            return found, attr_selector
                        except:
                            continue
        except:
            pass
        return None

    def _heal_by_position(
        self, driver, selector: str, element_type: str
    ) -> Optional[Tuple]:
        """Strategy 4: Find by position (nth-of-type)"""
        try:
            elements = driver.find_elements(By.TAG_NAME, element_type)

            # Try first few elements
            for i in range(min(5, len(elements))):
                nth_selector = f"{element_type}:nth-of-type({i+1})"
                try:
                    element = driver.find_element(By.CSS_SELECTOR, nth_selector)
                    # Verify it's visible and enabled
                    if element.is_displayed() and element.is_enabled():
                        return element, nth_selector
                except:
                    continue
        except:
            pass
        return None

    def _heal_by_similarity(
        self, driver, selector: str, element_type: str
    ) -> Optional[Tuple]:
        """Strategy 5: Find by class name similarity"""
        try:
            # Extract class names from original selector
            if "." in selector:
                original_classes = set()
                parts = selector.split(".")
                for part in parts[1:]:
                    class_name = part.split("[")[0].split(":")[0]
                    if class_name:
                        original_classes.add(class_name)

                if original_classes:
                    # Get all elements
                    elements = driver.find_elements(By.TAG_NAME, element_type)

                    best_match = None
                    best_score = 0

                    for element in elements:
                        classes = element.get_attribute("class")
                        if classes:
                            element_classes = set(classes.split())
                            # Calculate similarity
                            common = original_classes & element_classes
                            score = len(common) / len(original_classes)

                            if score > best_score and score > 0.5:
                                best_score = score
                                best_match = element

                    if best_match:
                        # Create selector from best match
                        classes = best_match.get_attribute("class")
                        if classes:
                            first_class = classes.split()[0]
                            healed_selector = f"{element_type}.{first_class}"
                            return best_match, healed_selector
        except:
            pass
        return None

    def _heal_by_parent_context(
        self, driver, selector: str, element_type: str
    ) -> Optional[Tuple]:
        """Strategy 6: Find by parent context"""
        try:
            # Try to find parent container first
            parent_selectors = [
                "form",
                "div.container",
                "div.content",
                "main",
                "section",
            ]

            for parent_sel in parent_selectors:
                try:
                    parent = driver.find_element(By.CSS_SELECTOR, parent_sel)
                    # Find element within parent
                    elements = parent.find_elements(By.TAG_NAME, element_type)
                    if elements:
                        # Try first visible element
                        for element in elements:
                            if element.is_displayed():
                                # Create contextual selector
                                healed_selector = f"{parent_sel} {element_type}"
                                return element, healed_selector
                except:
                    continue
        except:
            pass
        return None

    def _record_healing(self, original: str, healed: str, strategy: str):
        """Record healing event"""
        record = {
            "original_selector": original,
            "healed_selector": healed,
            "strategy": strategy,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }
        self.healing_history.append(record)

        # Update memory if available
        if self.memory:
            # This would integrate with the memory system
            pass

    def get_healing_stats(self) -> Dict:
        """Get healing statistics"""
        if not self.healing_history:
            return {
                "total_healings": 0,
                "unique_selectors_healed": 0,
                "success_rate": 0,
                "strategies_used": {},
            }

        strategies = defaultdict(int)
        for record in self.healing_history:
            strategies[record["strategy"]] += 1

        return {
            "total_healings": len(self.healing_history),
            "unique_selectors_healed": len(self.selector_mappings),
            "strategies_used": dict(strategies),
            "most_effective_strategy": (
                max(strategies.items(), key=lambda x: x[1])[0] if strategies else None
            ),
        }

    def get_selector_mapping(self, original: str) -> Optional[str]:
        """Get healed selector for original"""
        return self.selector_mappings.get(original)

    def print_healing_summary(self):
        """Print healing summary"""
        from colorama import Fore, Style

        stats = self.get_healing_stats()

        if stats["total_healings"] == 0:
            return

        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🔧 SELF-HEALING SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

        print(f"Total Healings: {stats['total_healings']}")
        print(f"Unique Selectors Healed: {stats['unique_selectors_healed']}")

        if stats["strategies_used"]:
            print(f"\n{Fore.YELLOW}Strategies Used:{Style.RESET_ALL}")
            for strategy, count in sorted(
                stats["strategies_used"].items(), key=lambda x: x[1], reverse=True
            ):
                strategy_name = (
                    strategy.replace("_heal_by_", "").replace("_", " ").title()
                )
                print(f"  • {strategy_name}: {count}")

        if stats["most_effective_strategy"]:
            strategy_name = (
                stats["most_effective_strategy"]
                .replace("_heal_by_", "")
                .replace("_", " ")
                .title()
            )
            print(f"\nMost Effective: {strategy_name}")

        # Show recent healings
        if self.healing_history:
            print(f"\n{Fore.YELLOW}Recent Healings:{Style.RESET_ALL}")
            for record in self.healing_history[-5:]:
                print(
                    f"  {record['original_selector'][:40]} → {record['healed_selector'][:40]}"
                )

        print()

    def export_mappings(self, filepath: str):
        """Export selector mappings to JSON"""
        import json
        from pathlib import Path

        data = {
            "mappings": self.selector_mappings,
            "history": self.healing_history,
            "stats": self.get_healing_stats(),
        }

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✓ Selector mappings exported: {filepath}")

    def import_mappings(self, filepath: str):
        """Import selector mappings from JSON"""
        import json
        from pathlib import Path

        if not Path(filepath).exists():
            print(f"✗ File not found: {filepath}")
            return

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.selector_mappings.update(data.get("mappings", {}))
        print(f"✓ Imported {len(data.get('mappings', {}))} selector mappings")
