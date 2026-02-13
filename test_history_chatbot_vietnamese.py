#!/usr/bin/env python3
"""
Test History Chatbot với tiếng Việt
Kiểm tra câu trả lời có đúng, bám sát câu hỏi, không lệch chủ đề
"""

import json
import os
import time
from datetime import datetime

import click
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from agent.cerebras_analyzer import CerebrasAnalyzer

load_dotenv()


class VietnameseHistoryChatbotTester:
    """Test chatbot lịch sử Việt Nam"""

    def __init__(self, url, headless=True):
        self.url = url
        self.headless = headless
        self.driver = None
        self.wait = None
        self.analyzer = CerebrasAnalyzer()
        self.results = []

        # Câu hỏi tiếng Việt về lịch sử
        self.test_questions = [
            {
                "question": "Ai là vua đầu tiên của Việt Nam?",
                "expected_keywords": [
                    "Đinh Tiên Hoàng",
                    "Đinh Bộ Lĩnh",
                    "968",
                    "Đại Cồ Việt",
                ],
                "category": "Lịch sử Việt Nam",
            },
            {
                "question": "Trận Bạch Đằng năm 1288 do ai chỉ huy?",
                "expected_keywords": ["Trần Hưng Đạo", "Trần Quốc Tuấn", "Mông Cổ"],
                "category": "Lịch sử Việt Nam",
            },
            {
                "question": "Cuộc khởi nghĩa Hai Bà Trưng diễn ra vào năm nào?",
                "expected_keywords": ["40", "Trưng Trắc", "Trưng Nhị", "Đông Hán"],
                "category": "Lịch sử Việt Nam",
            },
            {
                "question": "Ai là người sáng lập ra chữ Nôm?",
                "expected_keywords": ["chữ Nôm", "thế kỷ 13", "Việt Nam", "Hán tự"],
                "category": "Văn hóa Việt Nam",
            },
            {
                "question": "Triều đại nào tồn tại lâu nhất trong lịch sử Việt Nam?",
                "expected_keywords": ["Lê", "Lê Sơ", "Lê Trung흥", "1428", "1789"],
                "category": "Lịch sử Việt Nam",
            },
        ]

    def setup_driver(self):
        """Setup Chrome driver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--lang=vi-VN")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

        click.echo(click.style("✓ Driver setup complete", fg="green"))

    def teardown_driver(self):
        """Close driver"""
        if self.driver:
            if not self.headless:
                time.sleep(2)
            self.driver.quit()

    def find_input_element(self):
        """Tìm input field của chatbot"""
        # Thử các selector khác nhau
        selectors = [
            (By.CSS_SELECTOR, "textarea"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.CSS_SELECTOR, "input[placeholder*='nhập']"),
            (By.CSS_SELECTOR, "input[placeholder*='hỏi']"),
            (By.CSS_SELECTOR, "[contenteditable='true']"),
        ]

        for by, selector in selectors:
            try:
                elements = self.driver.find_elements(by, selector)
                for elem in elements:
                    if elem.is_displayed():
                        return elem
            except:
                continue

        return None

    def get_latest_response(self, question):
        """Lấy response mới nhất từ chatbot"""
        time.sleep(8)  # Đợi chatbot trả lời

        # Thử nhiều cách để lấy response
        methods = [
            # Method 1: Tìm message containers
            lambda: self._get_from_messages(),
            # Method 2: Tìm chat containers
            lambda: self._get_from_chats(),
            # Method 3: Lấy text mới từ body
            lambda: self._get_from_body(question),
        ]

        for method in methods:
            try:
                response = method()
                if response and len(response) > 50:  # Response phải có ít nhất 50 ký tự
                    return response
            except Exception as e:
                continue

        return None

    def _get_from_messages(self):
        """Lấy từ message containers"""
        messages = self.driver.find_elements(
            By.CSS_SELECTOR, "[class*='message'], [class*='Message']"
        )
        if messages:
            # Lấy message cuối cùng
            last_msg = messages[-1].text
            if last_msg and len(last_msg) > 20:
                return last_msg
        return None

    def _get_from_chats(self):
        """Lấy từ chat containers"""
        chats = self.driver.find_elements(
            By.CSS_SELECTOR, "[class*='chat'], [class*='Chat']"
        )
        if chats:
            last_chat = chats[-1].text
            if last_chat and len(last_chat) > 20:
                return last_chat
        return None

    def _get_from_body(self, question):
        """Lấy text mới từ body"""
        body_text = self.driver.find_element(By.TAG_NAME, "body").text

        # Tách phần sau câu hỏi
        if question in body_text:
            parts = body_text.split(question)
            if len(parts) > 1:
                response = parts[-1].strip()
                # Loại bỏ placeholder text
                if "Nhấn Enter" not in response and len(response) > 50:
                    return response[:1000]  # Giới hạn 1000 ký tự

        return None

    def validate_response_with_ai(self, question, response, expected_keywords):
        """Validate response với Cerebras AI"""
        prompt = f"""Đánh giá câu trả lời của chatbot lịch sử Việt Nam.

Câu hỏi: {question}
Câu trả lời: {response}
Từ khóa mong đợi: {', '.join(expected_keywords)}

Hãy đánh giá theo JSON format:
{{
  "is_correct": true/false,
  "is_relevant": true/false,
  "is_on_topic": true/false,
  "score": 0.0-1.0,
  "feedback_vi": "Nhận xét bằng tiếng Việt",
  "contains_keywords": ["keyword1", "keyword2"],
  "missing_keywords": ["keyword3"],
  "off_topic_reason": "Lý do lệch chủ đề (nếu có)"
}}

Tiêu chí đánh giá:
1. is_correct: Câu trả lời có đúng về mặt lịch sử không?
2. is_relevant: Câu trả lời có liên quan đến câu hỏi không?
3. is_on_topic: Câu trả lời có bám sát chủ đề không? Có lệch sang chủ đề khác không?
4. score: Điểm tổng thể từ 0.0 đến 1.0
5. feedback_vi: Nhận xét chi tiết bằng tiếng Việt

Trả về ONLY JSON, không có markdown.
"""

        try:
            response_obj = self.analyzer.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.analyzer.model_name,
                max_completion_tokens=1024,
                temperature=0.2,
                top_p=1,
                stream=False,
            )

            content = response_obj.choices[0].message.content

            # Remove markdown if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            return result

        except Exception as e:
            click.echo(click.style(f"⚠️ AI validation failed: {e}", fg="yellow"))
            return {
                "is_correct": False,
                "is_relevant": False,
                "is_on_topic": False,
                "score": 0.0,
                "feedback_vi": f"Lỗi validation: {e}",
                "contains_keywords": [],
                "missing_keywords": expected_keywords,
                "off_topic_reason": "Không thể đánh giá",
            }

    def run_tests(self):
        """Chạy test với các câu hỏi tiếng Việt"""
        click.echo("\n" + "=" * 80)
        click.echo(
            click.style("🇻🇳 TEST CHATBOT LỊCH SỬ VIỆT NAM", fg="cyan", bold=True)
        )
        click.echo("=" * 80)

        # Load page
        click.echo(f"\n📱 Loading {self.url}...")
        self.driver.get(self.url)
        time.sleep(5)

        # Find input
        input_element = self.find_input_element()
        if not input_element:
            click.echo(click.style("✗ Không tìm thấy input field!", fg="red"))
            return

        click.echo(click.style("✓ Đã tìm thấy input field", fg="green"))

        # Test each question
        for i, test in enumerate(self.test_questions, 1):
            question = test["question"]
            expected_keywords = test["expected_keywords"]
            category = test["category"]

            click.echo(f"\n{'='*80}")
            click.echo(
                click.style(f"📝 Test {i}/{len(self.test_questions)}", fg="cyan")
            )
            click.echo(f"Chủ đề: {category}")
            click.echo(f"Câu hỏi: {click.style(question, fg='yellow')}")

            try:
                # Clear và nhập câu hỏi
                input_element.clear()
                time.sleep(0.5)
                input_element.send_keys(question)
                time.sleep(0.5)

                # Nhấn Enter
                click.echo("⏎ Nhấn Enter...")
                input_element.send_keys(Keys.RETURN)

                # Đợi và lấy response
                click.echo("⏳ Đợi chatbot trả lời...")
                response = self.get_latest_response(question)

                if not response:
                    click.echo(click.style("✗ Không nhận được câu trả lời!", fg="red"))
                    self.results.append(
                        {
                            "test_id": i,
                            "question": question,
                            "category": category,
                            "response": None,
                            "error": "No response received",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    continue

                # Hiển thị response
                click.echo(f"\n💬 Câu trả lời:")
                click.echo(click.style(response[:500], fg="white"))
                if len(response) > 500:
                    click.echo(click.style("... (truncated)", fg="gray"))

                # Validate với AI
                click.echo("\n🤖 Đang đánh giá với AI...")
                validation = self.validate_response_with_ai(
                    question, response, expected_keywords
                )

                # Hiển thị kết quả
                click.echo(f"\n📊 Kết quả đánh giá:")
                click.echo(
                    f"  • Đúng: {click.style('✓' if validation['is_correct'] else '✗', fg='green' if validation['is_correct'] else 'red')}"
                )
                click.echo(
                    f"  • Liên quan: {click.style('✓' if validation['is_relevant'] else '✗', fg='green' if validation['is_relevant'] else 'red')}"
                )
                click.echo(
                    f"  • Bám sát chủ đề: {click.style('✓' if validation['is_on_topic'] else '✗', fg='green' if validation['is_on_topic'] else 'red')}"
                )
                click.echo(f"  • Điểm: {validation['score']:.2f}/1.0")
                click.echo(f"  • Nhận xét: {validation['feedback_vi']}")

                if validation.get("off_topic_reason"):
                    click.echo(
                        click.style(
                            f"  ⚠️ Lệch chủ đề: {validation['off_topic_reason']}",
                            fg="yellow",
                        )
                    )

                # Save result
                self.results.append(
                    {
                        "test_id": i,
                        "question": question,
                        "category": category,
                        "response": response[:500],
                        "validation": validation,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                # Đợi trước khi hỏi câu tiếp theo
                time.sleep(2)

            except Exception as e:
                click.echo(click.style(f"✗ Lỗi: {e}", fg="red"))
                self.results.append(
                    {
                        "test_id": i,
                        "question": question,
                        "category": category,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    def generate_report(self):
        """Tạo báo cáo"""
        click.echo("\n" + "=" * 80)
        click.echo(click.style("📊 BÁO CÁO KẾT QUẢ", fg="cyan", bold=True))
        click.echo("=" * 80)

        if not self.results:
            click.echo("Không có kết quả test")
            return

        # Tính toán thống kê
        total = len(self.results)
        correct = sum(
            1 for r in self.results if r.get("validation", {}).get("is_correct", False)
        )
        relevant = sum(
            1 for r in self.results if r.get("validation", {}).get("is_relevant", False)
        )
        on_topic = sum(
            1 for r in self.results if r.get("validation", {}).get("is_on_topic", False)
        )
        avg_score = (
            sum(r.get("validation", {}).get("score", 0) for r in self.results) / total
            if total > 0
            else 0
        )

        click.echo(f"\nTổng số câu hỏi: {total}")
        click.echo(
            click.style(
                f"Câu trả lời đúng: {correct}/{total} ({correct/total*100:.1f}%)",
                fg="green" if correct > total / 2 else "red",
            )
        )
        click.echo(
            click.style(
                f"Câu trả lời liên quan: {relevant}/{total} ({relevant/total*100:.1f}%)",
                fg="green" if relevant > total / 2 else "red",
            )
        )
        click.echo(
            click.style(
                f"Câu trả lời bám sát chủ đề: {on_topic}/{total} ({on_topic/total*100:.1f}%)",
                fg="green" if on_topic > total / 2 else "red",
            )
        )
        click.echo(f"Điểm trung bình: {avg_score:.2f}/1.0")

        # Save JSON report
        os.makedirs("reports", exist_ok=True)
        report_path = f"reports/vietnamese_history_test_{int(time.time())}.json"

        report_data = {
            "url": self.url,
            "timestamp": datetime.now().isoformat(),
            "language": "Vietnamese",
            "total_questions": total,
            "correct_answers": correct,
            "relevant_answers": relevant,
            "on_topic_answers": on_topic,
            "average_score": avg_score,
            "results": self.results,
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        click.echo(f"\n📄 Báo cáo đã lưu: {report_path}")

    def run(self):
        """Chạy toàn bộ test"""
        try:
            self.setup_driver()
            self.run_tests()
            self.generate_report()
        except Exception as e:
            click.echo(click.style(f"\n❌ Lỗi: {e}", fg="red"))
            import traceback

            traceback.print_exc()
        finally:
            self.teardown_driver()


@click.command()
@click.option(
    "--url",
    "-u",
    default="https://fe-history-mind-ai.vercel.app/",
    help="URL của chatbot",
)
@click.option(
    "--headless/--no-headless",
    default=True,
    help="Chạy ở chế độ headless (default: True)",
)
def main(url, headless):
    """
    Test Chatbot Lịch Sử Việt Nam

    Kiểm tra:
    - Câu trả lời có đúng không
    - Có bám sát câu hỏi không
    - Có lệch chủ đề không

    Examples:
        python test_history_chatbot_vietnamese.py
        python test_history_chatbot_vietnamese.py --no-headless
    """

    # Check API key
    if not os.environ.get("CEREBRAS_API_KEY"):
        click.echo(click.style("❌ Lỗi: Cần CEREBRAS_API_KEY!", fg="red", bold=True))
        click.echo("Thêm vào file .env: CEREBRAS_API_KEY=your_key")
        exit(1)

    click.echo("\n" + "=" * 80)
    click.echo(click.style("🇻🇳 TEST CHATBOT LỊCH SỬ VIỆT NAM", fg="green", bold=True))
    click.echo("=" * 80)
    click.echo(f"URL: {url}")
    click.echo(f"Headless: {headless}")
    click.echo(f"AI: Cerebras Cloud SDK (llama-3.3-70b)")
    click.echo("=" * 80)

    tester = VietnameseHistoryChatbotTester(url, headless)
    tester.run()


if __name__ == "__main__":
    main()
