#!/usr/bin/env python3
"""
Test chatbot động - tự động tạo nhiều test case
Chạy: python test.py
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from agent.cerebras_analyzer import CerebrasAnalyzer

load_dotenv()

# Cấu hình
URL = "https://fe-history-mind-ai.vercel.app/"
HEADLESS = False  # Hiển thị browser để xem


class TestCaseGenerator:
    """Tạo test case động cho chatbot lịch sử Việt Nam"""

    @staticmethod
    def generate_test_cases() -> List[Dict]:
        """Tạo danh sách test case động"""

        # Các category test
        categories = {
            "Nhân vật lịch sử": [
                {
                    "q": "Ai là vua đầu tiên của Việt Nam?",
                    "keywords": [
                        "Đinh Tiên Hoàng",
                        "Đinh Bộ Lĩnh",
                        "968",
                        "Đại Cồ Việt",
                    ],
                    "difficulty": "easy",
                },
                {
                    "q": "Trần Hưng Đạo là ai?",
                    "keywords": ["Trần Quốc Tuấn", "tướng", "Mông Cổ", "Bạch Đằng"],
                    "difficulty": "easy",
                },
                {
                    "q": "Lý Thường Kiệt nổi tiếng với chiến công nào?",
                    "keywords": ["Như Nguyệt", "Tống", "1075", "Nam quốc sơn hà"],
                    "difficulty": "medium",
                },
                {
                    "q": "Nguyễn Trãi có đóng góp gì cho lịch sử Việt Nam?",
                    "keywords": ["Bình Ngô đại cáo", "Lê Lợi", "Lam Sơn", "văn học"],
                    "difficulty": "medium",
                },
            ],
            "Sự kiện lịch sử": [
                {
                    "q": "Cuộc khởi nghĩa Hai Bà Trưng diễn ra vào năm nào?",
                    "keywords": ["40", "Trưng Trắc", "Trưng Nhị", "Đông Hán"],
                    "difficulty": "easy",
                },
                {
                    "q": "Trận Bạch Đằng năm 1288 do ai chỉ huy?",
                    "keywords": ["Trần Hưng Đạo", "Mông Cổ", "cọc ngầm"],
                    "difficulty": "easy",
                },
                {
                    "q": "Khởi nghĩa Lam Sơn diễn ra vào thời gian nào?",
                    "keywords": ["1418", "1427", "Lê Lợi", "Minh"],
                    "difficulty": "medium",
                },
                {
                    "q": "Chiến thắng Điện Biên Phủ có ý nghĩa gì?",
                    "keywords": ["1954", "Pháp", "Võ Nguyên Giáp", "độc lập"],
                    "difficulty": "medium",
                },
            ],
            "Triều đại": [
                {
                    "q": "Triều đại nào tồn tại lâu nhất trong lịch sử Việt Nam?",
                    "keywords": ["Lê", "1428", "1789", "361 năm"],
                    "difficulty": "hard",
                },
                {
                    "q": "Nhà Trần tồn tại từ năm nào đến năm nào?",
                    "keywords": ["1225", "1400", "175 năm"],
                    "difficulty": "medium",
                },
                {
                    "q": "Ai là người sáng lập nhà Lý?",
                    "keywords": ["Lý Công Uẩn", "Lý Thái Tổ", "1009", "Thăng Long"],
                    "difficulty": "easy",
                },
            ],
            "Văn hóa": [
                {
                    "q": "Chữ Nôm được tạo ra khi nào?",
                    "keywords": ["thế kỷ 13", "Hán tự", "Việt Nam", "chữ viết"],
                    "difficulty": "hard",
                },
                {
                    "q": "Văn Miếu Quốc Tử Giám được xây dựng vào năm nào?",
                    "keywords": ["1070", "Lý Thánh Tông", "giáo dục", "Hà Nội"],
                    "difficulty": "medium",
                },
            ],
            "Địa lý lịch sử": [
                {
                    "q": "Thăng Long được đổi tên thành Hà Nội vào năm nào?",
                    "keywords": ["1831", "Minh Mạng", "Nguyễn"],
                    "difficulty": "hard",
                },
                {
                    "q": "Kinh đô đầu tiên của Việt Nam sau độc lập là gì?",
                    "keywords": ["Hoa Lư", "Đinh", "Ninh Bình"],
                    "difficulty": "medium",
                },
            ],
            "Câu hỏi phức tạp": [
                {
                    "q": "So sánh chiến lược của Trần Hưng Đạo và Nguyễn Huệ trong việc đánh giặc?",
                    "keywords": [
                        "Trần Hưng Đạo",
                        "Nguyễn Huệ",
                        "chiến lược",
                        "du kích",
                    ],
                    "difficulty": "hard",
                },
                {
                    "q": "Tại sao Việt Nam có thể chống lại được các cuộc xâm lược của phương Bắc?",
                    "keywords": ["tinh thần", "địa hình", "chiến lược", "đoàn kết"],
                    "difficulty": "hard",
                },
            ],
            "Câu hỏi ngoài phạm vi": [
                {
                    "q": "Thời tiết hôm nay thế nào?",
                    "keywords": [],
                    "difficulty": "out_of_scope",
                    "expected_behavior": "refuse",
                },
                {
                    "q": "2 + 2 bằng mấy?",
                    "keywords": [],
                    "difficulty": "out_of_scope",
                    "expected_behavior": "refuse",
                },
            ],
        }

        # Flatten tất cả test cases
        all_tests = []
        for category, tests in categories.items():
            for test in tests:
                test["category"] = category
                all_tests.append(test)

        return all_tests


def main():
    print("\n" + "=" * 80)
    print("🇻🇳 TEST CHATBOT LỊCH SỬ VIỆT NAM - COMPREHENSIVE")
    print("=" * 80)

    # Check API key
    if not os.environ.get("CEREBRAS_API_KEY"):
        print("❌ Lỗi: Cần CEREBRAS_API_KEY trong file .env")
        return

    # Generate test cases
    generator = TestCaseGenerator()
    test_cases = generator.generate_test_cases()

    print(f"\n📋 Tổng số test case: {len(test_cases)}")

    # Count by category
    categories = {}
    for tc in test_cases:
        cat = tc["category"]
        categories[cat] = categories.get(cat, 0) + 1

    print("\n� Phân loại:")
    for cat, count in categories.items():
        print(f"  • {cat}: {count} test")

    # Setup browser
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=opts)
    analyzer = CerebrasAnalyzer()

    try:
        # Load page
        print(f"\n📱 Đang mở {URL}...")
        driver.get(URL)
        time.sleep(5)

        # Find input
        textarea = driver.find_element(By.TAG_NAME, "textarea")
        print("✓ Đã tìm thấy input")

        results = []
        stats = {
            "total": 0,
            "correct": 0,
            "relevant": 0,
            "on_topic": 0,
            "by_category": {},
            "by_difficulty": {},
        }

        # Test each question
        for i, test in enumerate(test_cases, 1):
            question = test["q"]
            keywords = test["keywords"]
            category = test["category"]
            difficulty = test.get("difficulty", "medium")
            expected_behavior = test.get("expected_behavior", "answer")

            print(f"\n{'='*80}")
            print(f"📝 Test {i}/{len(test_cases)}")
            print(f"Chủ đề: {category} | Độ khó: {difficulty}")
            print(f"Câu hỏi: {question}")

            # Type and send
            textarea.clear()
            time.sleep(0.5)
            textarea.send_keys(question)
            time.sleep(0.5)
            textarea.send_keys(Keys.RETURN)

            # Wait for response
            print("⏳ Đợi trả lời...")
            time.sleep(8)

            # Get response
            body_text = driver.find_element(By.TAG_NAME, "body").text
            if question in body_text:
                response = body_text.split(question)[-1][:800]
            else:
                response = "Không nhận được câu trả lời"

            print(f"💬 Trả lời: {response[:150]}...")

            # Validate
            print("🤖 Đánh giá...")
            prompt = f"""Đánh giá câu trả lời chatbot lịch sử Việt Nam.

Câu hỏi: {question}
Chủ đề: {category}
Độ khó: {difficulty}
Hành vi mong đợi: {expected_behavior}
Trả lời: {response}
Từ khóa mong đợi: {', '.join(keywords) if keywords else 'N/A'}

JSON format:
{{
  "correct": true/false,
  "relevant": true/false,
  "on_topic": true/false,
  "score": 0.0-1.0,
  "feedback": "Nhận xét ngắn gọn",
  "strengths": ["điểm mạnh 1", "điểm mạnh 2"],
  "weaknesses": ["điểm yếu 1", "điểm yếu 2"],
  "contains_keywords": ["keyword1", "keyword2"],
  "missing_keywords": ["keyword3"]
}}

Tiêu chí:
- correct: Đúng về mặt lịch sử
- relevant: Liên quan đến câu hỏi
- on_topic: Bám sát chủ đề, không lệch
- score: Điểm tổng thể 0-1

Nếu expected_behavior="refuse", chatbot nên từ chối trả lời câu hỏi ngoài phạm vi.

Chỉ trả JSON, không markdown."""

            try:
                resp = analyzer.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=analyzer.model_name,
                    max_completion_tokens=1024,
                    temperature=0.2,
                )

                content = resp.choices[0].message.content
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                validation = json.loads(content.strip())

                # Show result
                correct = "✓" if validation.get("correct") else "✗"
                relevant = "✓" if validation.get("relevant") else "✗"
                on_topic = "✓" if validation.get("on_topic") else "✗"
                score = validation.get("score", 0)

                print(
                    f"  Đúng: {correct} | Liên quan: {relevant} | Bám chủ đề: {on_topic} | Điểm: {score:.1f}"
                )
                print(f"  💡 {validation.get('feedback', '')}")

                # Update stats
                stats["total"] += 1
                if validation.get("correct"):
                    stats["correct"] += 1
                if validation.get("relevant"):
                    stats["relevant"] += 1
                if validation.get("on_topic"):
                    stats["on_topic"] += 1

                # Stats by category
                if category not in stats["by_category"]:
                    stats["by_category"][category] = {
                        "total": 0,
                        "correct": 0,
                        "score_sum": 0,
                    }
                stats["by_category"][category]["total"] += 1
                if validation.get("correct"):
                    stats["by_category"][category]["correct"] += 1
                stats["by_category"][category]["score_sum"] += score

                # Stats by difficulty
                if difficulty not in stats["by_difficulty"]:
                    stats["by_difficulty"][difficulty] = {
                        "total": 0,
                        "correct": 0,
                        "score_sum": 0,
                    }
                stats["by_difficulty"][difficulty]["total"] += 1
                if validation.get("correct"):
                    stats["by_difficulty"][difficulty]["correct"] += 1
                stats["by_difficulty"][difficulty]["score_sum"] += score

                results.append(
                    {
                        "test_id": i,
                        "question": question,
                        "category": category,
                        "difficulty": difficulty,
                        "expected_behavior": expected_behavior,
                        "response": response[:500],
                        "validation": validation,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                print(f"  ⚠️ Lỗi đánh giá: {e}")
                results.append(
                    {
                        "test_id": i,
                        "question": question,
                        "category": category,
                        "difficulty": difficulty,
                        "response": response[:500],
                        "error": str(e),
                    }
                )

            time.sleep(2)

        # Detailed Summary
        print("\n" + "=" * 80)
        print("📊 BÁO CÁO CHI TIẾT")
        print("=" * 80)

        total = stats["total"]
        print(f"\n🎯 TỔNG QUAN:")
        print(f"  Tổng số test: {total}")
        print(f"  Đúng: {stats['correct']}/{total} ({stats['correct']/total*100:.1f}%)")
        print(
            f"  Liên quan: {stats['relevant']}/{total} ({stats['relevant']/total*100:.1f}%)"
        )
        print(
            f"  Bám chủ đề: {stats['on_topic']}/{total} ({stats['on_topic']/total*100:.1f}%)"
        )

        print(f"\n📂 THEO CHỦ ĐỀ:")
        for cat, data in stats["by_category"].items():
            avg_score = data["score_sum"] / data["total"] if data["total"] > 0 else 0
            print(
                f"  • {cat}: {data['correct']}/{data['total']} đúng ({data['correct']/data['total']*100:.0f}%) - Điểm TB: {avg_score:.2f}"
            )

        print(f"\n⚡ THEO ĐỘ KHÓ:")
        for diff, data in stats["by_difficulty"].items():
            avg_score = data["score_sum"] / data["total"] if data["total"] > 0 else 0
            print(
                f"  • {diff}: {data['correct']}/{data['total']} đúng ({data['correct']/data['total']*100:.0f}%) - Điểm TB: {avg_score:.2f}"
            )

        # Save comprehensive report
        os.makedirs("reports", exist_ok=True)
        report_file = f"reports/comprehensive_test_{int(time.time())}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "url": URL,
                    "total_tests": total,
                    "statistics": stats,
                    "test_cases": results,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        print(f"\n📄 Báo cáo chi tiết: {report_file}")

        # Generate summary file
        summary_file = f"reports/summary_{int(time.time())}.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("BÁO CÁO TEST CHATBOT LỊCH SỬ VIỆT NAM\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"URL: {URL}\n")
            f.write(f"Tổng số test: {total}\n\n")

            f.write("TỔNG QUAN:\n")
            f.write(
                f"  Đúng: {stats['correct']}/{total} ({stats['correct']/total*100:.1f}%)\n"
            )
            f.write(
                f"  Liên quan: {stats['relevant']}/{total} ({stats['relevant']/total*100:.1f}%)\n"
            )
            f.write(
                f"  Bám chủ đề: {stats['on_topic']}/{total} ({stats['on_topic']/total*100:.1f}%)\n\n"
            )

            f.write("THEO CHỦ ĐỀ:\n")
            for cat, data in stats["by_category"].items():
                avg_score = (
                    data["score_sum"] / data["total"] if data["total"] > 0 else 0
                )
                f.write(
                    f"  {cat}: {data['correct']}/{data['total']} ({data['correct']/data['total']*100:.0f}%) - Điểm: {avg_score:.2f}\n"
                )

            f.write("\nTHEO ĐỘ KHÓ:\n")
            for diff, data in stats["by_difficulty"].items():
                avg_score = (
                    data["score_sum"] / data["total"] if data["total"] > 0 else 0
                )
                f.write(
                    f"  {diff}: {data['correct']}/{data['total']} ({data['correct']/data['total']*100:.0f}%) - Điểm: {avg_score:.2f}\n"
                )

        print(f"📄 Tóm tắt: {summary_file}")

    finally:
        if not HEADLESS:
            time.sleep(3)
        driver.quit()


if __name__ == "__main__":
    main()
