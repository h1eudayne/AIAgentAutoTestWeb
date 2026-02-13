#!/usr/bin/env python3
"""
Xem nội dung memory đã học được
"""

import json
from datetime import datetime
from pathlib import Path

from colorama import Fore, Style, init

init(autoreset=True)


def load_json(file_path):
    """Load JSON file"""
    if Path(file_path).exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def view_selector_memory():
    """Xem selector memory"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🎯 SELECTOR MEMORY{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    data = load_json("memory/selector_memory.json")

    if not data:
        print(
            f"{Fore.YELLOW}⚠️  Chưa có selector memory. Chạy test để tạo memory.{Style.RESET_ALL}"
        )
        return

    for page_hash, page_data in data.items():
        url = page_data.get("url", "Unknown")
        print(f"{Fore.GREEN}📄 Page: {url}{Style.RESET_ALL}")
        print(f"   Hash: {page_hash}")
        print(f"   Last updated: {page_data.get('last_updated', 'N/A')}")

        # Successful selectors
        selectors = page_data.get("selectors", {})
        if selectors:
            print(f"\n   {Fore.GREEN}✓ Successful Selectors:{Style.RESET_ALL}")
            for elem_type, selector_list in selectors.items():
                print(f"     {elem_type}:")
                for sel in sorted(
                    selector_list, key=lambda x: x.get("success_count", 0), reverse=True
                ):
                    count = sel.get("success_count", 0)
                    selector = sel.get("selector", "")
                    if len(selector) > 60:
                        selector = selector[:57] + "..."
                    print(f"       • {selector} (used {count} times)")

        # Failed selectors
        failed = page_data.get("failed_selectors", {})
        if failed:
            print(f"\n   {Fore.RED}✗ Failed Selectors:{Style.RESET_ALL}")
            for elem_type, fail_list in failed.items():
                if fail_list:
                    print(f"     {elem_type}:")
                    for fail in fail_list[-3:]:  # Show last 3 failures
                        selector = fail.get("selector", "")
                        if len(selector) > 60:
                            selector = selector[:57] + "..."
                        error = fail.get("error", "")[:40]
                        print(f"       • {selector} - {error}")

        print()


def view_test_history():
    """Xem test history"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📊 TEST HISTORY{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    data = load_json("memory/test_history.json")

    if not data:
        print(
            f"{Fore.YELLOW}⚠️  Chưa có test history. Chạy test để tạo history.{Style.RESET_ALL}"
        )
        return

    # Filter out session entries
    tests = [t for t in data if t.get("type") != "session"]
    sessions = [t for t in data if t.get("type") == "session"]

    print(f"Total tests: {len(tests)}")
    print(f"Total sessions: {len(sessions)}\n")

    if tests:
        # Group by URL
        by_url = {}
        for test in tests:
            url = test.get("url", "Unknown")
            if url not in by_url:
                by_url[url] = []
            by_url[url].append(test)

        for url, url_tests in by_url.items():
            print(f"{Fore.GREEN}📄 {url}{Style.RESET_ALL}")

            passed = sum(1 for t in url_tests if t.get("status") == "passed")
            failed = len(url_tests) - passed
            pass_rate = (passed / len(url_tests) * 100) if url_tests else 0

            print(f"   Total: {len(url_tests)} tests")
            print(f"   Passed: {Fore.GREEN}{passed}{Style.RESET_ALL}")
            print(f"   Failed: {Fore.RED}{failed}{Style.RESET_ALL}")
            print(f"   Pass rate: {pass_rate:.1f}%")

            # Show recent tests
            print(f"\n   Recent tests:")
            for test in url_tests[-5:]:
                status = test.get("status", "unknown")
                status_icon = "✓" if status == "passed" else "✗"
                status_color = Fore.GREEN if status == "passed" else Fore.RED
                name = test.get("test_name", "Unknown")
                if len(name) > 50:
                    name = name[:47] + "..."
                print(f"     {status_color}{status_icon}{Style.RESET_ALL} {name}")

            print()


def view_page_patterns():
    """Xem page patterns"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🔍 PAGE PATTERNS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    data = load_json("memory/page_patterns.json")

    if not data:
        print(
            f"{Fore.YELLOW}⚠️  Chưa có page patterns. Chạy test để tạo patterns.{Style.RESET_ALL}"
        )
        return

    for page_hash, pattern in data.items():
        url = pattern.get("url", "Unknown")
        print(f"{Fore.GREEN}📄 {url}{Style.RESET_ALL}")
        print(f"   Hash: {page_hash}")

        counts = pattern.get("element_counts", {})
        print(f"\n   Element counts:")
        print(f"     Buttons: {counts.get('buttons', 0)}")
        print(f"     Inputs: {counts.get('inputs', 0)}")
        print(f"     Links: {counts.get('links', 0)}")

        classes = pattern.get("common_classes", [])
        if classes:
            print(f"\n   Common CSS classes:")
            for cls in classes[:5]:
                print(f"     • {cls}")

        print(f"\n   Last seen: {pattern.get('last_seen', 'N/A')}")
        print()


def view_summary():
    """Tổng quan memory"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📈 MEMORY SUMMARY{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    selector_data = load_json("memory/selector_memory.json")
    test_data = load_json("memory/test_history.json")
    pattern_data = load_json("memory/page_patterns.json")

    print(f"Pages remembered: {len(selector_data) if selector_data else 0}")
    print(
        f"Tests in history: {len([t for t in test_data if t.get('type') != 'session']) if test_data else 0}"
    )
    print(f"Page patterns: {len(pattern_data) if pattern_data else 0}")

    # Calculate total memory size
    total_size = 0
    for file in [
        "memory/selector_memory.json",
        "memory/test_history.json",
        "memory/page_patterns.json",
    ]:
        if Path(file).exists():
            total_size += Path(file).stat().st_size

    print(f"Memory size: {total_size / 1024:.2f} KB")

    # Overall pass rate
    if test_data:
        tests = [t for t in test_data if t.get("type") != "session"]
        if tests:
            passed = sum(1 for t in tests if t.get("status") == "passed")
            pass_rate = passed / len(tests) * 100
            print(f"\nOverall pass rate: {pass_rate:.1f}%")


def main():
    print(f"\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}🧠 VIEW STATE MEMORY{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")

    # Check if memory exists
    if not Path("memory").exists():
        print(f"\n{Fore.RED}❌ Memory folder không tồn tại!{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}💡 Chạy test để tạo memory:{Style.RESET_ALL}")
        print("   python main_fast.py https://fe-history-mind-ai.vercel.app/")
        print()
        return

    view_summary()
    view_selector_memory()
    view_test_history()
    view_page_patterns()

    print(f"\n{Fore.GREEN}✅ Xem xong memory!{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}💡 Tips:{Style.RESET_ALL}")
    print("  • Chạy test nhiều lần để memory học nhiều hơn")
    print("  • Memory sẽ giúp agent test nhanh và chính xác hơn")
    print("  • Pass rate sẽ tăng dần qua mỗi lần test")
    print()


if __name__ == "__main__":
    main()
