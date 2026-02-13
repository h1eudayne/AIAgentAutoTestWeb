# Accessibility Checker - Basic WCAG compliance checks
from typing import List, Dict
from colorama import Fore, Style


class AccessibilityChecker:
    """Basic accessibility checks"""

    def __init__(self):
        self.issues = []

    def check_images_alt_text(self, driver) -> List[Dict]:
        """Check if images have alt text"""
        images = driver.find_elements("tag name", "img")
        issues = []

        for img in images:
            alt = img.get_attribute("alt")
            if not alt:
                issues.append(
                    {
                        "type": "missing_alt",
                        "element": "img",
                        "src": img.get_attribute("src"),
                    }
                )

        self.issues.extend(issues)
        return issues

    def check_form_labels(self, driver) -> List[Dict]:
        """Check if form inputs have labels"""
        inputs = driver.find_elements("tag name", "input")
        issues = []

        for inp in inputs:
            label_id = inp.get_attribute("id")
            if label_id:
                labels = driver.find_elements(
                    "css selector", f"label[for='{label_id}']"
                )
                if not labels:
                    issues.append(
                        {"type": "missing_label", "element": "input", "id": label_id}
                    )

        self.issues.extend(issues)
        return issues

    def print_summary(self):
        """Print accessibility summary"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}♿ ACCESSIBILITY SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

        if not self.issues:
            print(f"{Fore.GREEN}✓ No accessibility issues found{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Found {len(self.issues)} issues:{Style.RESET_ALL}")
            for issue in self.issues[:10]:
                print(
                    f"  • {issue['type']}: {issue.get('src', issue.get('id', 'N/A'))}"
                )
        print()
