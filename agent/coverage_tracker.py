# Coverage Tracker - Track test coverage
import json
from typing import Dict, List, Set, Optional
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class CoverageTracker:
    """
    Coverage Tracker - Theo dõi test coverage
    Track which elements, pages, and features have been tested
    """

    def __init__(self, output_dir: str = "reports/coverage"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Track coverage
        self.pages_tested = set()
        self.elements_tested = defaultdict(set)  # page -> set of selectors
        self.actions_tested = defaultdict(
            lambda: defaultdict(int)
        )  # page -> action -> count
        self.features_tested = set()

        # Track test results
        self.test_results = []
        self.element_success_rate = defaultdict(lambda: {"success": 0, "fail": 0})

        # Coverage goals
        self.coverage_goals = {
            "pages": set(),
            "critical_elements": set(),
            "features": set(),
        }

    def set_coverage_goals(
        self,
        pages: List[str] = None,
        critical_elements: List[str] = None,
        features: List[str] = None,
    ):
        """
        Set coverage goals
        """
        if pages:
            self.coverage_goals["pages"] = set(pages)
        if critical_elements:
            self.coverage_goals["critical_elements"] = set(critical_elements)
        if features:
            self.coverage_goals["features"] = set(features)

    def track_page(self, url: str):
        """Track that a page was tested"""
        self.pages_tested.add(url)

    def track_element(self, page: str, selector: str, action: str, success: bool):
        """
        Track that an element was tested

        Args:
            page: Page URL
            selector: Element selector
            action: Action performed (click, type, etc.)
            success: Whether action succeeded
        """
        self.elements_tested[page].add(selector)
        self.actions_tested[page][action] += 1

        # Track success rate
        key = f"{page}::{selector}"
        if success:
            self.element_success_rate[key]["success"] += 1
        else:
            self.element_success_rate[key]["fail"] += 1

    def track_feature(self, feature: str):
        """Track that a feature was tested"""
        self.features_tested.add(feature)

    def track_test_result(
        self,
        test_name: str,
        page: str,
        elements_tested: List[str],
        actions: List[str],
        success: bool,
    ):
        """
        Track complete test result
        """
        result = {
            "test_name": test_name,
            "page": page,
            "elements_count": len(elements_tested),
            "actions_count": len(actions),
            "success": success,
            "timestamp": datetime.now().isoformat(),
        }

        self.test_results.append(result)

        # Update coverage
        self.track_page(page)
        for element in elements_tested:
            for action in actions:
                self.track_element(page, element, action, success)

    def get_page_coverage(self) -> Dict:
        """Get page coverage statistics"""
        total_goals = len(self.coverage_goals["pages"])
        tested = (
            len(self.pages_tested & self.coverage_goals["pages"])
            if total_goals > 0
            else len(self.pages_tested)
        )

        coverage_pct = (tested / total_goals * 100) if total_goals > 0 else 100

        return {
            "total_pages_tested": len(self.pages_tested),
            "goal_pages": total_goals,
            "goal_pages_tested": tested,
            "coverage_percentage": round(coverage_pct, 1),
            "untested_pages": (
                list(self.coverage_goals["pages"] - self.pages_tested)
                if total_goals > 0
                else []
            ),
        }

    def get_element_coverage(self) -> Dict:
        """Get element coverage statistics"""
        total_elements = sum(
            len(elements) for elements in self.elements_tested.values()
        )

        # Calculate success rate
        total_success = sum(
            data["success"] for data in self.element_success_rate.values()
        )
        total_attempts = sum(
            data["success"] + data["fail"]
            for data in self.element_success_rate.values()
        )
        success_rate = (
            (total_success / total_attempts * 100) if total_attempts > 0 else 0
        )

        return {
            "total_elements_tested": total_elements,
            "pages_with_elements": len(self.elements_tested),
            "avg_elements_per_page": round(
                total_elements / max(len(self.elements_tested), 1), 1
            ),
            "element_success_rate": round(success_rate, 1),
            "total_attempts": total_attempts,
        }

    def get_action_coverage(self) -> Dict:
        """Get action coverage statistics"""
        all_actions = defaultdict(int)
        for page_actions in self.actions_tested.values():
            for action, count in page_actions.items():
                all_actions[action] += count

        total_actions = sum(all_actions.values())

        return {
            "total_actions": total_actions,
            "action_types": len(all_actions),
            "actions_breakdown": dict(all_actions),
            "most_common_action": (
                max(all_actions.items(), key=lambda x: x[1])[0] if all_actions else None
            ),
        }

    def get_feature_coverage(self) -> Dict:
        """Get feature coverage statistics"""
        total_goals = len(self.coverage_goals["features"])
        tested = (
            len(self.features_tested & self.coverage_goals["features"])
            if total_goals > 0
            else len(self.features_tested)
        )

        coverage_pct = (tested / total_goals * 100) if total_goals > 0 else 100

        return {
            "total_features_tested": len(self.features_tested),
            "goal_features": total_goals,
            "goal_features_tested": tested,
            "coverage_percentage": round(coverage_pct, 1),
            "untested_features": (
                list(self.coverage_goals["features"] - self.features_tested)
                if total_goals > 0
                else []
            ),
        }

    def get_overall_coverage(self) -> Dict:
        """Get overall coverage summary"""
        page_cov = self.get_page_coverage()
        element_cov = self.get_element_coverage()
        action_cov = self.get_action_coverage()
        feature_cov = self.get_feature_coverage()

        # Calculate overall score
        scores = []
        if page_cov["goal_pages"] > 0:
            scores.append(page_cov["coverage_percentage"])
        if feature_cov["goal_features"] > 0:
            scores.append(feature_cov["coverage_percentage"])
        if element_cov["element_success_rate"] > 0:
            scores.append(element_cov["element_success_rate"])

        overall_score = sum(scores) / len(scores) if scores else 0

        return {
            "overall_score": round(overall_score, 1),
            "page_coverage": page_cov["coverage_percentage"],
            "feature_coverage": feature_cov["coverage_percentage"],
            "element_success_rate": element_cov["element_success_rate"],
            "total_tests": len(self.test_results),
            "total_actions": action_cov["total_actions"],
        }

    def get_coverage_gaps(self) -> Dict:
        """Identify coverage gaps"""
        gaps = {
            "untested_pages": [],
            "untested_features": [],
            "low_coverage_pages": [],
            "failing_elements": [],
        }

        # Untested pages
        if self.coverage_goals["pages"]:
            gaps["untested_pages"] = list(
                self.coverage_goals["pages"] - self.pages_tested
            )

        # Untested features
        if self.coverage_goals["features"]:
            gaps["untested_features"] = list(
                self.coverage_goals["features"] - self.features_tested
            )

        # Low coverage pages (< 50% success rate)
        for page, elements in self.elements_tested.items():
            page_success = 0
            page_total = 0
            for element in elements:
                key = f"{page}::{element}"
                if key in self.element_success_rate:
                    data = self.element_success_rate[key]
                    page_success += data["success"]
                    page_total += data["success"] + data["fail"]

            if page_total > 0:
                success_rate = page_success / page_total
                if success_rate < 0.5:
                    gaps["low_coverage_pages"].append(
                        {"page": page, "success_rate": round(success_rate * 100, 1)}
                    )

        # Failing elements (success rate < 50%)
        for key, data in self.element_success_rate.items():
            total = data["success"] + data["fail"]
            if total > 0:
                success_rate = data["success"] / total
                if success_rate < 0.5:
                    page, selector = key.split("::", 1)
                    gaps["failing_elements"].append(
                        {
                            "page": page,
                            "selector": selector,
                            "success_rate": round(success_rate * 100, 1),
                            "attempts": total,
                        }
                    )

        return gaps

    def save_report(self, filename: Optional[str] = None) -> str:
        """Save coverage report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"coverage_report_{timestamp}.json"

        filepath = self.output_dir / filename

        report = {
            "summary": self.get_overall_coverage(),
            "page_coverage": self.get_page_coverage(),
            "element_coverage": self.get_element_coverage(),
            "action_coverage": self.get_action_coverage(),
            "feature_coverage": self.get_feature_coverage(),
            "coverage_gaps": self.get_coverage_gaps(),
            "test_results": self.test_results[-50:],  # Last 50 tests
            "timestamp": datetime.now().isoformat(),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📊 Coverage report saved: {filepath}")
        return str(filepath)

    def print_summary(self):
        """Print coverage summary to console"""
        from colorama import Fore, Style

        overall = self.get_overall_coverage()
        page_cov = self.get_page_coverage()
        element_cov = self.get_element_coverage()
        action_cov = self.get_action_coverage()
        feature_cov = self.get_feature_coverage()
        gaps = self.get_coverage_gaps()

        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 TEST COVERAGE SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

        # Overall score
        score = overall["overall_score"]
        score_color = (
            Fore.GREEN if score >= 80 else Fore.YELLOW if score >= 60 else Fore.RED
        )
        print(f"{score_color}Overall Coverage Score: {score}%{Style.RESET_ALL}\n")

        # Page coverage
        print(f"{Fore.YELLOW}Page Coverage:{Style.RESET_ALL}")
        print(f"  Pages Tested: {page_cov['total_pages_tested']}")
        if page_cov["goal_pages"] > 0:
            print(
                f"  Goal Pages: {page_cov['goal_pages_tested']}/{page_cov['goal_pages']} ({page_cov['coverage_percentage']}%)"
            )

        # Element coverage
        print(f"\n{Fore.YELLOW}Element Coverage:{Style.RESET_ALL}")
        print(f"  Elements Tested: {element_cov['total_elements_tested']}")
        print(f"  Success Rate: {element_cov['element_success_rate']}%")
        print(f"  Avg Elements/Page: {element_cov['avg_elements_per_page']}")

        # Action coverage
        print(f"\n{Fore.YELLOW}Action Coverage:{Style.RESET_ALL}")
        print(f"  Total Actions: {action_cov['total_actions']}")
        print(f"  Action Types: {action_cov['action_types']}")
        if action_cov["actions_breakdown"]:
            print(f"  Breakdown:")
            for action, count in sorted(
                action_cov["actions_breakdown"].items(),
                key=lambda x: x[1],
                reverse=True,
            ):
                print(f"    • {action}: {count}")

        # Feature coverage
        if feature_cov["goal_features"] > 0:
            print(f"\n{Fore.YELLOW}Feature Coverage:{Style.RESET_ALL}")
            print(
                f"  Features Tested: {feature_cov['goal_features_tested']}/{feature_cov['goal_features']} ({feature_cov['coverage_percentage']}%)"
            )

        # Coverage gaps
        if any(gaps.values()):
            print(f"\n{Fore.RED}Coverage Gaps:{Style.RESET_ALL}")

            if gaps["untested_pages"]:
                print(f"  Untested Pages: {len(gaps['untested_pages'])}")
                for page in gaps["untested_pages"][:3]:
                    print(f"    • {page}")

            if gaps["untested_features"]:
                print(f"  Untested Features: {len(gaps['untested_features'])}")
                for feature in gaps["untested_features"][:3]:
                    print(f"    • {feature}")

            if gaps["failing_elements"]:
                print(f"  Failing Elements: {len(gaps['failing_elements'])}")
                for elem in gaps["failing_elements"][:3]:
                    print(f"    • {elem['selector']} ({elem['success_rate']}% success)")

        print()
