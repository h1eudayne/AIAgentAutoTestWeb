#!/usr/bin/env python3
"""
Test chatbot đơn giản - chỉ cần chạy: python test.py
"""

import json
import os
import time
from datetime import datetime

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

# Câu hỏi test
QUESTIONS = [
    {
        "q": "Ai là vua đầu tiên của Việt Nam?",
        "keywords": ["Đinh Tiên Hoàng", "Đinh Bộ Lĩnh", "968"],
    },
    {
        "q": "Trận Bạch Đằng năm 1288 do ai chỉ huy?",
        "keywords": ["Trần Hưng Đạo", "Trần Quốc Tuấn"],
    },
    {
        "q": "Cuộc khởi nghĩa Hai Bà Trưng diễn ra vào năm nào?",
        "keywords": ["40", "Trưng Trắc", "Trưng Nhị"],
    },
]


def main():
    print("\n" + "=" * 80)
    print("🇻🇳 TEST CHATBOT LỊCH SỬ VIỆT NAM")
    print("=" * 80)

    # Check API key
    if not os.environ.get("CEREBRAS_API_KEY"):
        print("❌ Lỗi: Cần CEREBRAS_API_KEY trong file .env")
        return

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

        # Test each question
        for i, test in enumerate(QUESTIONS, 1):
            question = test["q"]
            keywords = test["keywords"]

            print(f"\n{'='*80}")
            print(f"📝 Câu {i}/{len(QUESTIONS)}: {question}")

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
                response = body_text.split(question)[-1][:500]
            else:
                response = "Không nhận được câu trả lời"

            print(f"💬 Trả lời: {response[:200]}...")

            # Validate
            print("🤖 Đánh giá...")
            prompt = f"""Đánh giá câu trả lời chatbot lịch sử.

Câu hỏi: {question}
Trả lời: {response}
Từ khóa: {', '.join(keywords)}

JSON format:
{{
  "correct": true/false,
  "relevant": true/false,
  "score": 0-1,
  "feedback": "Nhận xét ngắn"
}}

Chỉ trả JSON, không markdown."""

            try:
                resp = analyzer.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=analyzer.model_name,
                    max_completion_tokens=512,
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
                score = validation.get("score", 0)

                print(f"  Đúng: {correct} | Liên quan: {relevant} | Điểm: {score:.1f}")
                print(f"  {validation.get('feedback', '')}")

                results.append(
                    {
                        "question": question,
                        "response": response[:200],
                        "validation": validation,
                    }
                )

            except Exception as e:
                print(f"  ⚠️ Lỗi đánh giá: {e}")
                results.append({"question": question, "response": response[:200]})

            time.sleep(2)

        # Summary
        print("\n" + "=" * 80)
        print("📊 KẾT QUẢ")
        print("=" * 80)

        total = len(results)
        correct = sum(1 for r in results if r.get("validation", {}).get("correct"))
        relevant = sum(1 for r in results if r.get("validation", {}).get("relevant"))

        print(f"Tổng: {total} câu")
        print(f"Đúng: {correct}/{total} ({correct/total*100:.0f}%)")
        print(f"Liên quan: {relevant}/{total} ({relevant/total*100:.0f}%)")

        # Save report
        os.makedirs("reports", exist_ok=True)
        report_file = f"reports/test_{int(time.time())}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "total": total,
                    "correct": correct,
                    "relevant": relevant,
                    "results": results,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        print(f"\n📄 Báo cáo: {report_file}")

    finally:
        if not HEADLESS:
            time.sleep(3)
        driver.quit()


if __name__ == "__main__":
    main()
