# Result Analyzer
from datetime import datetime
from typing import Dict, List


class ResultAnalyzer:
    def __init__(self):
        self.analysis = {}

    def analyze_results(self, results: List[Dict]) -> Dict:
        """Phân tích kết quả test"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "summary": self._calculate_summary(results),
            "failures": self._extract_failures(results),
            "recommendations": self._generate_recommendations(results),
        }

        self.analysis = analysis
        return analysis

    def _calculate_summary(self, results: List[Dict]) -> Dict:
        total = len(results)
        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = total - passed

        high_priority_failed = sum(
            1
            for r in results
            if r.get("status") == "failed" and r.get("priority") == "high"
        )

        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
            "high_priority_failures": high_priority_failed,
        }

    def _extract_failures(self, results: List[Dict]) -> List[Dict]:
        """Trích xuất các test thất bại"""
        failures = []

        for result in results:
            if result.get("status") == "failed":
                failures.append(
                    {
                        "test_name": result.get("name"),
                        "priority": result.get("priority"),
                        "errors": result.get("errors", []),
                        "failed_step": self._find_failed_step(result.get("steps", [])),
                    }
                )

        return failures

    def _find_failed_step(self, steps: List[Dict]) -> Dict:
        """Tìm bước thất bại"""
        for i, step in enumerate(steps, 1):
            if not step.get("success"):
                return {
                    "step_number": i,
                    "action": step.get("action"),
                    "error": step.get("error"),
                }
        return {}

    def _generate_recommendations(self, results: List[Dict]) -> List[str]:
        """Sinh khuyến nghị dựa trên kết quả"""
        recommendations = []

        failures = [r for r in results if r.get("status") == "failed"]

        if not failures:
            recommendations.append(
                "✅ All tests passed! Web application is functioning correctly."
            )
            return recommendations

        # Phân tích lỗi phổ biến
        error_types = {}
        for failure in failures:
            for error in failure.get("errors", []):
                error_lower = error.lower()
                if "timeout" in error_lower:
                    error_types["timeout"] = error_types.get("timeout", 0) + 1
                elif "not found" in error_lower or "no such element" in error_lower:
                    error_types["element_not_found"] = (
                        error_types.get("element_not_found", 0) + 1
                    )
                elif "click" in error_lower:
                    error_types["click_failed"] = error_types.get("click_failed", 0) + 1

        # Khuyến nghị dựa trên lỗi
        if error_types.get("timeout", 0) > 0:
            recommendations.append(
                f"⚠️ {error_types['timeout']} timeout errors detected. "
                "Consider increasing wait times or checking page load performance."
            )

        if error_types.get("element_not_found", 0) > 0:
            recommendations.append(
                f"⚠️ {error_types['element_not_found']} element not found errors. "
                "Selectors may need updating or elements are dynamically loaded."
            )

        if error_types.get("click_failed", 0) > 0:
            recommendations.append(
                f"⚠️ {error_types['click_failed']} click failures. "
                "Elements may be obscured or not clickable."
            )

        # Khuyến nghị về priority
        high_priority_failures = sum(1 for f in failures if f.get("priority") == "high")
        if high_priority_failures > 0:
            recommendations.append(
                f"🔴 {high_priority_failures} high-priority tests failed. "
                "These should be addressed immediately."
            )

        return recommendations
