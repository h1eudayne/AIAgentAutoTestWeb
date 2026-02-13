# State Memory System - Agent learns from past tests
import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class StateMemory:
    """
    State Memory System - Lưu trữ và học từ các test trước đó
    """

    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)

        # Memory files
        self.selector_memory_file = self.memory_dir / "selector_memory.json"
        self.test_history_file = self.memory_dir / "test_history.json"
        self.page_patterns_file = self.memory_dir / "page_patterns.json"

        # Load existing memory
        self.selector_memory = self._load_json(self.selector_memory_file, {})
        self.test_history = self._load_json(self.test_history_file, [])
        self.page_patterns = self._load_json(self.page_patterns_file, {})

        # Runtime cache
        self.current_session = {
            "start_time": datetime.now().isoformat(),
            "actions": [],
            "successful_selectors": {},
            "failed_selectors": {},
        }

    def _load_json(self, file_path: Path, default):
        """Load JSON file"""
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return default
        return default

    def _save_json(self, file_path: Path, data):
        """Save JSON file"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_page_hash(self, url: str) -> str:
        """Generate hash for page URL"""
        return hashlib.md5(url.encode()).hexdigest()[:12]

    def remember_successful_selector(
        self, url: str, element_type: str, selector: str, context: Dict = None
    ):
        """
        Ghi nhớ selector thành công
        """
        page_hash = self.get_page_hash(url)

        if page_hash not in self.selector_memory:
            self.selector_memory[page_hash] = {
                "url": url,
                "selectors": {},
                "last_updated": datetime.now().isoformat(),
            }

        if element_type not in self.selector_memory[page_hash]["selectors"]:
            self.selector_memory[page_hash]["selectors"][element_type] = []

        # Add selector with success count
        selector_entry = {
            "selector": selector,
            "success_count": 1,
            "last_used": datetime.now().isoformat(),
            "context": context or {},
        }

        # Check if selector already exists
        existing = None
        for i, s in enumerate(
            self.selector_memory[page_hash]["selectors"][element_type]
        ):
            if s["selector"] == selector:
                existing = i
                break

        if existing is not None:
            # Increment success count
            self.selector_memory[page_hash]["selectors"][element_type][existing][
                "success_count"
            ] += 1
            self.selector_memory[page_hash]["selectors"][element_type][existing][
                "last_used"
            ] = datetime.now().isoformat()
        else:
            # Add new selector
            self.selector_memory[page_hash]["selectors"][element_type].append(
                selector_entry
            )

        # Update session
        self.current_session["successful_selectors"][selector] = (
            self.current_session["successful_selectors"].get(selector, 0) + 1
        )

        # Save to disk
        self._save_json(self.selector_memory_file, self.selector_memory)

    def remember_failed_selector(
        self, url: str, element_type: str, selector: str, error: str
    ):
        """
        Ghi nhớ selector thất bại
        """
        page_hash = self.get_page_hash(url)

        if page_hash not in self.selector_memory:
            self.selector_memory[page_hash] = {
                "url": url,
                "selectors": {},
                "failed_selectors": {},
                "last_updated": datetime.now().isoformat(),
            }

        if "failed_selectors" not in self.selector_memory[page_hash]:
            self.selector_memory[page_hash]["failed_selectors"] = {}

        if element_type not in self.selector_memory[page_hash]["failed_selectors"]:
            self.selector_memory[page_hash]["failed_selectors"][element_type] = []

        # Add failed selector
        failed_entry = {
            "selector": selector,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        }

        self.selector_memory[page_hash]["failed_selectors"][element_type].append(
            failed_entry
        )

        # Update session
        self.current_session["failed_selectors"][selector] = error

        # Save to disk
        self._save_json(self.selector_memory_file, self.selector_memory)

    def get_best_selectors(
        self, url: str, element_type: str, limit: int = 5
    ) -> List[str]:
        """
        Lấy các selector tốt nhất từ memory
        Sắp xếp theo success_count
        """
        page_hash = self.get_page_hash(url)

        if page_hash not in self.selector_memory:
            return []

        if element_type not in self.selector_memory[page_hash].get("selectors", {}):
            return []

        selectors = self.selector_memory[page_hash]["selectors"][element_type]

        # Sort by success_count
        sorted_selectors = sorted(
            selectors, key=lambda x: x["success_count"], reverse=True
        )

        return [s["selector"] for s in sorted_selectors[:limit]]

    def should_avoid_selector(self, url: str, element_type: str, selector: str) -> bool:
        """
        Kiểm tra xem có nên tránh selector này không
        """
        page_hash = self.get_page_hash(url)

        if page_hash not in self.selector_memory:
            return False

        failed_selectors = (
            self.selector_memory[page_hash]
            .get("failed_selectors", {})
            .get(element_type, [])
        )

        # Check if selector failed recently (within last 10 attempts)
        recent_failures = [
            f for f in failed_selectors[-10:] if f["selector"] == selector
        ]

        return len(recent_failures) >= 3  # Avoid if failed 3+ times recently

    def remember_test_result(self, url: str, test_case: Dict, result: Dict):
        """
        Ghi nhớ kết quả test
        """
        test_entry = {
            "url": url,
            "test_name": test_case.get("name"),
            "priority": test_case.get("priority"),
            "status": result.get("status"),
            "timestamp": datetime.now().isoformat(),
            "steps": len(test_case.get("steps", [])),
            "errors": result.get("errors", []),
        }

        self.test_history.append(test_entry)

        # Keep only last 1000 tests
        if len(self.test_history) > 1000:
            self.test_history = self.test_history[-1000:]

        # Save to disk
        self._save_json(self.test_history_file, self.test_history)

    def get_test_statistics(self, url: Optional[str] = None) -> Dict:
        """
        Thống kê test history
        """
        if url:
            tests = [
                t
                for t in self.test_history
                if t.get("url") == url and t.get("type") != "session"
            ]
        else:
            tests = [t for t in self.test_history if t.get("type") != "session"]

        if not tests:
            return {"total": 0, "passed": 0, "failed": 0, "pass_rate": "0%"}

        total = len(tests)
        passed = sum(1 for t in tests if t.get("status") == "passed")
        failed = total - passed

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{passed/total*100:.1f}%",
        }

    def learn_page_pattern(self, url: str, page_info: Dict):
        """
        Học pattern của page (element types, structure)
        """
        page_hash = self.get_page_hash(url)

        pattern = {
            "url": url,
            "element_counts": {
                "buttons": len(
                    [
                        e
                        for e in page_info.get("elements", [])
                        if e.get("tag") == "button"
                    ]
                ),
                "inputs": len(
                    [
                        e
                        for e in page_info.get("elements", [])
                        if e.get("tag") == "input"
                    ]
                ),
                "links": len(
                    [e for e in page_info.get("elements", []) if e.get("tag") == "a"]
                ),
            },
            "common_classes": self._extract_common_classes(
                page_info.get("elements", [])
            ),
            "last_seen": datetime.now().isoformat(),
        }

        self.page_patterns[page_hash] = pattern
        self._save_json(self.page_patterns_file, self.page_patterns)

    def _extract_common_classes(self, elements: List[Dict]) -> List[str]:
        """Extract most common CSS classes"""
        class_counts = defaultdict(int)

        for elem in elements:
            classes = elem.get("class", "").split()
            for cls in classes:
                if cls:
                    class_counts[cls] += 1

        # Return top 10 most common classes
        sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
        return [cls for cls, count in sorted_classes[:10]]

    def get_similar_pages(self, url: str, limit: int = 3) -> List[Dict]:
        """
        Tìm các page tương tự dựa trên pattern
        """
        page_hash = self.get_page_hash(url)

        if page_hash not in self.page_patterns:
            return []

        current_pattern = self.page_patterns[page_hash]
        similar = []

        for other_hash, other_pattern in self.page_patterns.items():
            if other_hash == page_hash:
                continue

            # Calculate similarity score
            similarity = self._calculate_similarity(current_pattern, other_pattern)

            if similarity > 0.5:  # 50% similar
                similar.append(
                    {
                        "url": other_pattern["url"],
                        "similarity": similarity,
                        "pattern": other_pattern,
                    }
                )

        # Sort by similarity
        similar.sort(key=lambda x: x["similarity"], reverse=True)

        return similar[:limit]

    def _calculate_similarity(self, pattern1: Dict, pattern2: Dict) -> float:
        """Calculate similarity between two page patterns"""
        counts1 = pattern1.get("element_counts", {})
        counts2 = pattern2.get("element_counts", {})

        # Compare element counts
        total_diff = 0
        total_sum = 0

        for key in ["buttons", "inputs", "links"]:
            val1 = counts1.get(key, 0)
            val2 = counts2.get(key, 0)
            total_diff += abs(val1 - val2)
            total_sum += val1 + val2

        if total_sum == 0:
            return 0

        count_similarity = 1 - (total_diff / total_sum)

        # Compare common classes
        classes1 = set(pattern1.get("common_classes", []))
        classes2 = set(pattern2.get("common_classes", []))

        if classes1 or classes2:
            class_similarity = len(classes1 & classes2) / len(classes1 | classes2)
        else:
            class_similarity = 0

        # Weighted average
        return 0.6 * count_similarity + 0.4 * class_similarity

    def get_recommendations(self, url: str) -> Dict:
        """
        Đưa ra khuyến nghị dựa trên memory
        """
        page_hash = self.get_page_hash(url)
        recommendations = {
            "best_selectors": {},
            "avoid_selectors": {},
            "similar_pages": [],
            "test_stats": {},
        }

        # Best selectors
        for element_type in ["button", "input", "link"]:
            best = self.get_best_selectors(url, element_type, limit=3)
            if best:
                recommendations["best_selectors"][element_type] = best

        # Similar pages
        recommendations["similar_pages"] = self.get_similar_pages(url, limit=3)

        # Test statistics
        recommendations["test_stats"] = self.get_test_statistics(url)

        return recommendations

    def save_session(self):
        """Save current session to history"""
        self.current_session["end_time"] = datetime.now().isoformat()

        # Add to test history
        session_summary = {
            "type": "session",
            "start_time": self.current_session["start_time"],
            "end_time": self.current_session["end_time"],
            "total_actions": len(self.current_session["actions"]),
            "successful_selectors": len(self.current_session["successful_selectors"]),
            "failed_selectors": len(self.current_session["failed_selectors"]),
        }

        self.test_history.append(session_summary)
        self._save_json(self.test_history_file, self.test_history)

    def clear_memory(self, older_than_days: int = 30):
        """
        Xóa memory cũ hơn X ngày
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=older_than_days)

        # Filter test history
        self.test_history = [
            t
            for t in self.test_history
            if datetime.fromisoformat(t["timestamp"]) > cutoff_date
        ]

        self._save_json(self.test_history_file, self.test_history)

        print(f"✓ Cleared memory older than {older_than_days} days")

    def get_memory_stats(self) -> Dict:
        """
        Thống kê memory
        """
        return {
            "total_pages_remembered": len(self.selector_memory),
            "total_tests_in_history": len(self.test_history),
            "total_page_patterns": len(self.page_patterns),
            "current_session_actions": len(self.current_session["actions"]),
            "memory_size_kb": sum(
                os.path.getsize(f)
                for f in [
                    self.selector_memory_file,
                    self.test_history_file,
                    self.page_patterns_file,
                ]
                if f.exists()
            )
            / 1024,
        }
