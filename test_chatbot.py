#!/usr/bin/env python3
"""
Chatbot Testing Agent - Test kiến thức lịch sử Việt Nam
"""

import json
import sys
import time
from datetime import datetime

from colorama import Fore, Style, init

from tools.browser import BrowserController

init(autoreset=True)


class ChatbotTester:
    def __init__(self, headless: bool = False):
        print(f"{Fore.CYAN}🤖 Initializing Chatbot Testing Agent...{Style.RESET_ALL}\n")
        self.browser = BrowserController(headless=headless, timeout=60)
        self.test_results = []

    def get_test_questions(self):
        """Danh sách câu hỏi test về lịch sử Việt Nam"""
        return [
            # Triều đại Trần
            {
                "category": "Triều đại Trần",
                "question": "Hãy kể cho tôi về triều đại nhà Trần",
                "keywords": ["Trần", "1225", "Thăng Long", "Mông Cổ"],
                "priority": "high",
            },
            {
                "category": "Triều đại Trần",
                "question": "Trần Hưng Đạo là ai?",
                "keywords": ["Trần Hưng Đạo", "tướng", "Mông Cổ", "chiến thắng"],
                "priority": "high",
            },
            {
                "category": "Triều đại Trần",
                "question": "Triều đại Trần tồn tại bao lâu?",
                "keywords": ["1225", "1400", "năm"],
                "priority": "medium",
            },
            # Hai Bà Trưng
            {
                "category": "Hai Bà Trưng",
                "question": "Ai là Hai Bà Trưng và cuộc khởi nghĩa của họ?",
                "keywords": ["Trưng Trắc", "Trưng Nhị", "khởi nghĩa", "40"],
                "priority": "high",
            },
            {
                "category": "Hai Bà Trưng",
                "question": "Hai Bà Trưng khởi nghĩa chống ai?",
                "keywords": ["Hán", "Trung Quốc", "Tô Định"],
                "priority": "high",
            },
            {
                "category": "Hai Bà Trưng",
                "question": "Cuộc khởi nghĩa Hai Bà Trưng diễn ra năm nào?",
                "keywords": ["40", "năm"],
                "priority": "medium",
            },
            # Văn Miếu
            {
                "category": "Văn Miếu",
                "question": "Văn Miếu - Quốc Tử Giám có lịch sử như thế nào?",
                "keywords": ["Văn Miếu", "1070", "Lý Thánh Tông", "giáo dục"],
                "priority": "high",
            },
            {
                "category": "Văn Miếu",
                "question": "Văn Miếu được xây dựng để làm gì?",
                "keywords": ["Khổng Tử", "giáo dục", "học", "thi"],
                "priority": "medium",
            },
            {
                "category": "Văn Miếu",
                "question": "Văn Miếu ở đâu?",
                "keywords": ["Hà Nội", "Thăng Long"],
                "priority": "low",
            },
            # Đại Việt
            {
                "category": "Đại Việt",
                "question": "Đại Việt đã được thành lập như thế nào?",
                "keywords": ["Đại Việt", "1054", "Lý Thánh Tông"],
                "priority": "high",
            },
            {
                "category": "Đại Việt",
                "question": "Tên nước Đại Việt có ý nghĩa gì?",
                "keywords": ["Đại Việt", "Việt Nam", "tên nước"],
                "priority": "medium",
            },
            # Lý Thái Tổ
            {
                "category": "Nhà Lý",
                "question": "Lý Thái Tổ là ai?",
                "keywords": ["Lý Thái Tổ", "Lý Công Uẩn", "1009", "Thăng Long"],
                "priority": "high",
            },
            {
                "category": "Nhà Lý",
                "question": "Lý Thái Tổ dời đô về đâu?",
                "keywords": ["Thăng Long", "Hà Nội", "1010"],
                "priority": "medium",
            },
            # Ngô Quyền
            {
                "category": "Ngô Quyền",
                "question": "Ngô Quyền đánh thắng ai ở sông Bạch Đằng?",
                "keywords": ["Nam Hán", "Bạch Đằng", "938", "cọc"],
                "priority": "high",
            },
            # Lê Lợi
            {
                "category": "Lê Lợi",
                "question": "Lê Lợi khởi nghĩa Lam Sơn là gì?",
                "keywords": ["Lê Lợi", "Lam Sơn", "Minh", "1418"],
                "priority": "high",
            },
            # Tổng hợp
            {
                "category": "Tổng hợp",
                "question": "Những triều đại nào trong lịch sử Việt Nam?",
                "keywords": ["Lý", "Trần", "Lê", "Nguyễn"],
                "priority": "medium",
            },
            {
                "category": "Tổng hợp",
                "question": "Ai là những anh hùng dân tộc Việt Nam?",
                "keywords": ["Trần Hưng Đạo", "Lê Lợi", "Hai Bà Trưng", "Ngô Quyền"],
                "priority": "medium",
            },
        ]

    def click_button_and_wait(self, button_text: str, wait_time: int = 3):
        """Click button và đợi response"""
        try:
            # Tìm button chứa text
            buttons = self.browser.driver.find_elements("tag name", "button")
            for btn in buttons:
                if button_text.lower() in btn.text.lower():
                    print(f"  📍 Clicking button: {btn.text[:50]}")
                    btn.click()
                    time.sleep(wait_time)
                    return True

            print(f"  ⚠️ Button not found: {button_text}")
            return False
        except Exception as e:
            print(f"  ❌ Error clicking button: {e}")
            return False

    def get_chat_response(self):
        """Lấy response từ chatbot"""
        try:
            time.sleep(2)  # Đợi response load

            # Lấy toàn bộ text trên page
            page_text = self.browser.driver.find_element("tag name", "body").text

            # Tìm phần response (thường là text dài nhất hoặc trong div chat)
            # Có thể cần điều chỉnh selector tùy theo cấu trúc web
            return page_text

        except Exception as e:
            print(f"  ❌ Error getting response: {e}")
            return ""

    def check_keywords(self, response: str, keywords: list) -> dict:
        """Kiểm tra keywords có trong response không"""
        response_lower = response.lower()
        found_keywords = []
        missing_keywords = []

        for keyword in keywords:
            if keyword.lower() in response_lower:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)

        accuracy = len(found_keywords) / len(keywords) * 100 if keywords else 0

        return {
            "found": found_keywords,
            "missing": missing_keywords,
            "accuracy": accuracy,
            "passed": accuracy >= 50,  # Pass nếu tìm thấy >= 50% keywords
        }

    def test_question(self, test_case: dict, index: int, total: int):
        """Test một câu hỏi"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}[Test {index}/{total}] Category: {test_case['category']}{Style.RESET_ALL}"
        )
        print(f"{Fore.YELLOW}❓ Question: {test_case['question']}{Style.RESET_ALL}")
        print(f"   Priority: {test_case['priority']}")
        print(f"   Expected keywords: {', '.join(test_case['keywords'])}")

        result = {
            "index": index,
            "category": test_case["category"],
            "question": test_case["question"],
            "priority": test_case["priority"],
            "expected_keywords": test_case["keywords"],
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # Click button tương ứng với category
            button_clicked = self.click_button_and_wait(test_case["category"])

            if not button_clicked:
                result["status"] = "failed"
                result["error"] = "Button not found"
                result["response"] = ""
                result["keyword_check"] = {"accuracy": 0, "passed": False}
                print(f"{Fore.RED}✗ FAILED: Button not found{Style.RESET_ALL}")
                return result

            # Lấy response
            print(f"  ⏳ Waiting for response...")
            response = self.get_chat_response()

            # Lấy 500 ký tự đầu của response để hiển thị
            response_preview = response[:500] if len(response) > 500 else response
            print(f"\n  {Fore.GREEN}💬 Response (preview):{Style.RESET_ALL}")
            print(f"  {response_preview}...")

            # Kiểm tra keywords
            keyword_check = self.check_keywords(response, test_case["keywords"])

            result["status"] = "passed" if keyword_check["passed"] else "failed"
            result["response"] = response
            result["response_length"] = len(response)
            result["keyword_check"] = keyword_check

            # Hiển thị kết quả
            print(f"\n  {Fore.CYAN}📊 Keyword Analysis:{Style.RESET_ALL}")
            print(f"     Accuracy: {keyword_check['accuracy']:.1f}%")
            print(
                f"     Found: {', '.join(keyword_check['found']) if keyword_check['found'] else 'None'}"
            )
            print(
                f"     Missing: {', '.join(keyword_check['missing']) if keyword_check['missing'] else 'None'}"
            )

            if keyword_check["passed"]:
                print(f"\n  {Fore.GREEN}✓ PASSED{Style.RESET_ALL}")
            else:
                print(f"\n  {Fore.RED}✗ FAILED (Low accuracy){Style.RESET_ALL}")

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["response"] = ""
            result["keyword_check"] = {"accuracy": 0, "passed": False}
            print(f"{Fore.RED}✗ ERROR: {e}{Style.RESET_ALL}")

        return result

    def test_chatbot(self, url: str):
        """Test toàn bộ chatbot"""
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🤖 CHATBOT KNOWLEDGE TESTING{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

        try:
            # Navigate
            print(f"{Fore.YELLOW}📍 Navigating to: {url}{Style.RESET_ALL}")
            if not self.browser.navigate(url):
                print(f"{Fore.RED}❌ Failed to load website{Style.RESET_ALL}")
                return
            print(f"{Fore.GREEN}✓ Page loaded{Style.RESET_ALL}\n")

            # Get test questions
            test_cases = self.get_test_questions()
            total = len(test_cases)

            print(f"{Fore.CYAN}📋 Total test cases: {total}{Style.RESET_ALL}\n")

            # Run tests
            for i, test_case in enumerate(test_cases, 1):
                result = self.test_question(test_case, i, total)
                self.test_results.append(result)

                # Navigate back to home if needed
                if i < total:
                    print(f"\n  ⏳ Preparing for next test...")
                    self.browser.navigate(url)
                    time.sleep(2)

            # Generate report
            self.generate_report(url)

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️ Testing interrupted by user{Style.RESET_ALL}")
            self.generate_report(url)
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
            import traceback

            traceback.print_exc()
        finally:
            self.cleanup()

    def generate_report(self, url: str):
        """Tạo báo cáo chi tiết"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 CHATBOT TEST REPORT{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

        # Calculate statistics
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.get("status") == "passed")
        failed = sum(1 for r in self.test_results if r.get("status") == "failed")
        errors = sum(1 for r in self.test_results if r.get("status") == "error")

        avg_accuracy = (
            sum(
                r.get("keyword_check", {}).get("accuracy", 0) for r in self.test_results
            )
            / total
            if total > 0
            else 0
        )

        # Summary
        print(f"{Fore.YELLOW}📍 URL:{Style.RESET_ALL} {url}")
        print(
            f"{Fore.YELLOW}⏰ Time:{Style.RESET_ALL} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        print(f"{Fore.CYAN}📊 SUMMARY{Style.RESET_ALL}")
        print(f"  Total Tests: {total}")
        print(
            f"  {Fore.GREEN}✓ Passed: {passed} ({passed/total*100:.1f}%){Style.RESET_ALL}"
        )
        print(
            f"  {Fore.RED}✗ Failed: {failed} ({failed/total*100:.1f}%){Style.RESET_ALL}"
        )
        print(f"  {Fore.YELLOW}⚠ Errors: {errors}{Style.RESET_ALL}")
        print(f"  Average Accuracy: {avg_accuracy:.1f}%\n")

        # By category
        categories = {}
        for r in self.test_results:
            cat = r.get("category", "Unknown")
            if cat not in categories:
                categories[cat] = {"total": 0, "passed": 0, "accuracy": []}
            categories[cat]["total"] += 1
            if r.get("status") == "passed":
                categories[cat]["passed"] += 1
            categories[cat]["accuracy"].append(
                r.get("keyword_check", {}).get("accuracy", 0)
            )

        print(f"{Fore.CYAN}📋 BY CATEGORY{Style.RESET_ALL}")
        for cat, stats in categories.items():
            avg_acc = (
                sum(stats["accuracy"]) / len(stats["accuracy"])
                if stats["accuracy"]
                else 0
            )
            pass_rate = stats["passed"] / stats["total"] * 100
            print(f"  {cat}:")
            print(
                f"    Pass rate: {pass_rate:.1f}% ({stats['passed']}/{stats['total']})"
            )
            print(f"    Avg accuracy: {avg_acc:.1f}%")

        # Failed tests
        failed_tests = [r for r in self.test_results if r.get("status") != "passed"]
        if failed_tests:
            print(f"\n{Fore.RED}❌ FAILED/ERROR TESTS{Style.RESET_ALL}")
            for r in failed_tests:
                print(f"  • [{r['category']}] {r['question']}")
                print(f"    Status: {r['status']}")
                if r.get("error"):
                    print(f"    Error: {r['error']}")
                else:
                    kw = r.get("keyword_check", {})
                    print(f"    Accuracy: {kw.get('accuracy', 0):.1f}%")
                    print(f"    Missing keywords: {', '.join(kw.get('missing', []))}")

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"reports/chatbot_test_{timestamp}.json"

        report_data = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "0%",
                "avg_accuracy": f"{avg_accuracy:.1f}%",
            },
            "by_category": {
                cat: {
                    "total": stats["total"],
                    "passed": stats["passed"],
                    "pass_rate": f"{stats['passed']/stats['total']*100:.1f}%",
                    "avg_accuracy": f"{sum(stats['accuracy'])/len(stats['accuracy']):.1f}%",
                }
                for cat, stats in categories.items()
            },
            "results": self.test_results,
        }

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\n{Fore.GREEN}✓ Report saved to: {report_file}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    def cleanup(self):
        """Clean up"""
        print(f"{Fore.CYAN}🧹 Cleaning up...{Style.RESET_ALL}")
        self.browser.close()
        print(f"{Fore.GREEN}✓ Done{Style.RESET_ALL}\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Chatbot Knowledge Testing Agent")
    parser.add_argument("url", help="URL của chatbot")
    parser.add_argument("--headless", action="store_true", help="Chạy headless mode")

    args = parser.parse_args()

    if not args.url.startswith(("http://", "https://")):
        args.url = "https://" + args.url

    tester = ChatbotTester(headless=args.headless)
    tester.test_chatbot(args.url)


if __name__ == "__main__":
    main()
