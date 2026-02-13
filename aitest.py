#!/usr/bin/env python3
"""
AI Web Testing CLI - Test bất kỳ website nào với AI
Usage: python aitest.py --url https://example.com --lang vi
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import click
from dotenv import load_dotenv, set_key
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Load environment
load_dotenv()


# Language translations
TRANSLATIONS = {
    "vi": {
        "setup_title": "🤖 THIẾT LẬP AI PROVIDER",
        "choose_provider": "Chọn AI provider",
        "enter_api_key": "📝 Nhập {} API key:",
        "get_key_at": "   Lấy key tại: {}",
        "api_key_prompt": "API Key",
        "save_to_env": "Lưu vào .env file?",
        "saved": "✓ Đã lưu vào {}",
        "existing_key": "✓ Đã có API key: {}...",
        "use_this_key": "Dùng key này?",
        "enter_url": "🌐 Nhập URL cần test",
        "url_label": "✓ URL: {}",
        "provider_label": "✓ AI Provider: {}",
        "provider_ready": "✓ AI provider sẵn sàng",
        "error": "✗ Lỗi: {}",
        "starting_browser": "🌐 Đang khởi động browser...",
        "loading": "📱 Đang tải {}...",
        "analyzing": "🔍 Phân tích website với AI...",
        "analyzing_progress": "Đang phân tích",
        "type_label": "✓ Loại: {}",
        "description_label": "✓ Mô tả: {}",
        "generating_tests": "🧪 Tạo test cases...",
        "generating_progress": "Đang tạo",
        "no_tests": "✗ Không tạo được test cases",
        "generated_tests": "✓ Đã tạo {} test cases",
        "test_cases_title": "📋 Test cases:",
        "and_more": "  ... và {} test nữa",
        "run_tests": "▶️  Chạy tests?",
        "aborted": "Đã hủy",
        "running_tests": "Đang chạy tests",
        "results_title": "📊 KẾT QUẢ",
        "total": "Tổng",
        "correct": "Đúng",
        "relevant": "Liên quan",
        "report": "📄 Báo cáo: {}",
        "choose_language": "Chọn ngôn ngữ test",
        "language_label": "✓ Ngôn ngữ: {}",
    },
    "en": {
        "setup_title": "🤖 AI PROVIDER SETUP",
        "choose_provider": "Choose AI provider",
        "enter_api_key": "📝 Enter {} API key:",
        "get_key_at": "   Get key at: {}",
        "api_key_prompt": "API Key",
        "save_to_env": "Save to .env file?",
        "saved": "✓ Saved to {}",
        "existing_key": "✓ Existing API key: {}...",
        "use_this_key": "Use this key?",
        "enter_url": "🌐 Enter URL to test",
        "url_label": "✓ URL: {}",
        "provider_label": "✓ AI Provider: {}",
        "provider_ready": "✓ AI provider ready",
        "error": "✗ Error: {}",
        "starting_browser": "🌐 Starting browser...",
        "loading": "📱 Loading {}...",
        "analyzing": "🔍 Analyzing website with AI...",
        "analyzing_progress": "Analyzing",
        "type_label": "✓ Type: {}",
        "description_label": "✓ Description: {}",
        "generating_tests": "🧪 Generating test cases...",
        "generating_progress": "Generating",
        "no_tests": "✗ No test cases generated",
        "generated_tests": "✓ Generated {} test cases",
        "test_cases_title": "📋 Test cases:",
        "and_more": "  ... and {} more",
        "run_tests": "▶️  Run tests?",
        "aborted": "Aborted",
        "running_tests": "Running tests",
        "results_title": "📊 RESULTS",
        "total": "Total",
        "correct": "Correct",
        "relevant": "Relevant",
        "report": "📄 Report: {}",
        "choose_language": "Choose test language",
        "language_label": "✓ Language: {}",
    },
}


def t(key: str, lang: str = "en") -> str:
    """Get translation"""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


class AIProvider:
    """Base class for AI providers"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def analyze_website(self, html: str, url: str) -> Dict:
        raise NotImplementedError

    def generate_test_cases(self, analysis: Dict) -> Dict:
        raise NotImplementedError

    def validate_response(
        self, question: str, response: str, keywords: List[str]
    ) -> Dict:
        raise NotImplementedError


class CerebrasProvider(AIProvider):
    """Cerebras Cloud SDK Provider"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        from cerebras.cloud.sdk import Cerebras

        self.client = Cerebras(api_key=api_key)
        self.model = "llama-3.3-70b"

    def _call_api(self, prompt: str, max_tokens: int = 1024) -> str:
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            max_completion_tokens=max_tokens,
            temperature=0.2,
        )
        content = response.choices[0].message.content
        # Clean markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        return content.strip()

    def analyze_website(self, html: str, url: str) -> Dict:
        prompt = f"""Analyze this website and determine its type.

URL: {url}
HTML: {html[:5000]}

Return JSON:
{{
  "type": "chatbot|ecommerce|blog|portfolio|form|dashboard|documentation|social_media|other",
  "description": "Brief description",
  "key_features": ["feature1", "feature2"],
  "primary_interactions": ["interaction1", "interaction2"]
}}

Only JSON, no markdown."""

        try:
            content = self._call_api(prompt)
            return json.loads(content)
        except:
            return {"type": "other", "description": "Unknown", "key_features": []}

    def generate_test_cases(self, analysis: Dict, language: str = "en") -> List[Dict]:
        website_type = analysis.get("type", "other")
        description = analysis.get("description", "")

        # Language-specific instructions
        lang_instruction = {
            "vi": "Tạo câu hỏi bằng TIẾNG VIỆT. Câu hỏi phải phù hợp với văn hóa và ngữ cảnh Việt Nam.",
            "en": "Generate questions in ENGLISH. Questions should be clear and natural.",
        }.get(language, "Generate questions in English.")

        prompt = f"""Generate test cases for this website.

Type: {website_type}
Description: {description}
Language: {language.upper()}

{lang_instruction}

Return JSON array of test cases:
[
  {{
    "question": "Test question or action in {language.upper()}",
    "keywords": ["keyword1", "keyword2"],
    "category": "Category name",
    "difficulty": "easy|medium|hard"
  }}
]

Generate 10-15 relevant test cases based on website type.
IMPORTANT: All questions MUST be in {language.upper()} language.
Only JSON array, no markdown."""

        try:
            content = self._call_api(prompt, max_tokens=2048)
            return json.loads(content)
        except:
            return []

    def validate_response(
        self, question: str, response: str, keywords: List[str]
    ) -> Dict:
        prompt = f"""Evaluate this response.

Question: {question}
Response: {response}
Expected keywords: {', '.join(keywords)}

Return JSON:
{{
  "correct": true/false,
  "relevant": true/false,
  "on_topic": true/false,
  "score": 0.0-1.0,
  "feedback": "Brief feedback"
}}

Only JSON, no markdown."""

        try:
            content = self._call_api(prompt, max_tokens=512)
            return json.loads(content)
        except:
            return {
                "correct": False,
                "relevant": False,
                "on_topic": False,
                "score": 0.0,
                "feedback": "Validation failed",
            }


class GeminiProvider(AIProvider):
    """Google Gemini Provider"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        from google import genai
        from google.genai import types

        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"
        self.types = types

    def _call_api(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=self.types.GenerateContentConfig(
                temperature=0.3, response_mime_type="application/json"
            ),
        )
        return response.text

    def analyze_website(self, html: str, url: str) -> Dict:
        prompt = f"""Analyze website type.
URL: {url}
HTML: {html[:5000]}
Return JSON with type, description, key_features."""
        try:
            return json.loads(self._call_api(prompt))
        except:
            return {"type": "other", "description": "Unknown", "key_features": []}

    def generate_test_cases(self, analysis: Dict, language: str = "en") -> List[Dict]:
        lang_instruction = {
            "vi": "Tạo câu hỏi bằng TIẾNG VIỆT",
            "en": "Generate questions in ENGLISH",
        }.get(language, "Generate questions in English")

        prompt = f"""Generate 10-15 test cases for {analysis.get('type')} website.
{lang_instruction}.
Return JSON array with question, keywords, category, difficulty."""
        try:
            return json.loads(self._call_api(prompt))
        except:
            return []

    def validate_response(
        self, question: str, response: str, keywords: List[str]
    ) -> Dict:
        prompt = f"""Evaluate: Q: {question}, A: {response}, Keywords: {keywords}
Return JSON with correct, relevant, on_topic, score, feedback."""
        try:
            return json.loads(self._call_api(prompt))
        except:
            return {"correct": False, "relevant": False, "score": 0.0}


def get_api_key(provider: str, lang: str = "en") -> str:
    """Get API key for provider"""
    env_var = "CEREBRAS_API_KEY" if provider == "cerebras" else "GEMINI_API_KEY"
    existing_key = os.environ.get(env_var)

    if existing_key:
        click.echo(f"\n{t('existing_key', lang).format(existing_key[:20])}")
        if click.confirm(t("use_this_key", lang), default=True):
            return existing_key

    # Prompt for new key
    click.echo(f"\n{t('enter_api_key', lang).format(provider.upper())}")
    if provider == "cerebras":
        click.echo(t("get_key_at", lang).format("https://cloud.cerebras.ai/"))
    else:
        click.echo(
            t("get_key_at", lang).format("https://aistudio.google.com/app/apikey")
        )

    api_key = click.prompt(t("api_key_prompt", lang), hide_input=True)

    # Save to .env
    env_file = Path(".env")
    if click.confirm(f"\n{t('save_to_env', lang)}", default=True):
        set_key(env_file, env_var, api_key)
        click.echo(click.style(t("saved", lang).format(env_file), fg="green"))

    return api_key


def create_provider(provider_name: str, api_key: str) -> AIProvider:
    """Create AI provider instance"""
    if provider_name == "cerebras":
        return CerebrasProvider(api_key)
    elif provider_name == "gemini":
        return GeminiProvider(api_key)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


@click.command()
@click.option("--url", "-u", help="URL to test")
@click.option(
    "--lang",
    "-l",
    type=click.Choice(["vi", "en"], case_sensitive=False),
    prompt="🌍 Choose test language / Chọn ngôn ngữ",
    help="Test language (vi=Vietnamese, en=English)",
)
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["cerebras", "gemini"], case_sensitive=False),
    prompt="🤖 Choose AI provider / Chọn AI provider",
    help="AI provider",
)
@click.option("--headless/--no-headless", default=True, help="Headless mode")
@click.option("--api-key", help="API key (optional, will prompt if needed)")
def main(url, lang, provider, headless, api_key):
    """
    🚀 AI Web Testing CLI - Test any website with AI

    Examples:
        python aitest.py --url https://example.com
        python aitest.py -u https://chatbot.com --no-headless
    """

    click.echo("\n" + "=" * 80)
    click.echo(click.style("🚀 AI WEB TESTING CLI", fg="green", bold=True))
    click.echo("=" * 80)

    lang_name = "Tiếng Việt" if lang == "vi" else "English"
    click.echo(f"\n✓ {t('language_label', lang).format(lang_name)}")

    # Get URL
    if not url:
        url = click.prompt(f"\n{t('enter_url', lang)}")

    if not url.startswith("http"):
        url = "https://" + url

    click.echo(f"\n{t('url_label', lang).format(url)}")

    # Get API key if not provided
    if not api_key:
        api_key = get_api_key(provider, lang)

    click.echo(f"\n{t('provider_label', lang).format(provider.upper())}")

    # Create provider
    try:
        ai = create_provider(provider, api_key)
        click.echo(click.style("✓ AI provider ready", fg="green"))
    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg="red"))
        return

    # Setup browser
    click.echo("\n🌐 Starting browser...")
    opts = Options()
    if headless:
        opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=opts)

    try:
        # Load page
        click.echo(f"📱 Loading {url}...")
        driver.get(url)
        time.sleep(3)

        html = driver.page_source

        # Analyze website
        click.echo("\n🔍 Analyzing website with AI...")
        with click.progressbar(length=100, label="Analyzing") as bar:
            analysis = ai.analyze_website(html, url)
            bar.update(100)

        website_type = analysis.get("type", "unknown")
        description = analysis.get("description", "")

        click.echo(f"\n✓ Type: {click.style(website_type, fg='yellow', bold=True)}")
        click.echo(f"✓ Description: {description}")

        # Generate test cases
        click.echo("\n🧪 Generating test cases...")
        with click.progressbar(length=100, label="Generating") as bar:
            test_cases = ai.generate_test_cases(analysis)
            bar.update(100)

        if not test_cases:
            click.echo(click.style("✗ No test cases generated", fg="red"))
            return

        click.echo(f"\n✓ Generated {len(test_cases)} test cases")

        # Show test cases
        click.echo("\n📋 Test cases:")
        for i, tc in enumerate(test_cases[:5], 1):
            click.echo(f"  {i}. {tc.get('question', 'N/A')}")
        if len(test_cases) > 5:
            click.echo(f"  ... and {len(test_cases) - 5} more")

        # Confirm to run tests
        if not click.confirm("\n▶️  Run tests?", default=True):
            click.echo("Aborted")
            return

        # Run tests
        results = []
        stats = {"total": 0, "correct": 0, "relevant": 0}

        with click.progressbar(
            test_cases,
            label="Running tests",
            item_show_func=lambda x: x.get("question", "")[:50] if x else "",
        ) as bar:
            for tc in bar:
                question = tc.get("question", "")
                keywords = tc.get("keywords", [])

                # Find input
                try:
                    textarea = driver.find_element(By.TAG_NAME, "textarea")
                except:
                    try:
                        textarea = driver.find_element(
                            By.CSS_SELECTOR, "input[type='text']"
                        )
                    except:
                        continue

                # Send question
                textarea.clear()
                time.sleep(0.5)
                textarea.send_keys(question)
                time.sleep(0.5)
                textarea.send_keys(Keys.RETURN)
                time.sleep(5)

                # Get response
                body_text = driver.find_element(By.TAG_NAME, "body").text
                response = (
                    body_text.split(question)[-1][:500]
                    if question in body_text
                    else "No response"
                )

                # Validate
                validation = ai.validate_response(question, response, keywords)

                stats["total"] += 1
                if validation.get("correct"):
                    stats["correct"] += 1
                if validation.get("relevant"):
                    stats["relevant"] += 1

                results.append(
                    {
                        "question": question,
                        "response": response[:200],
                        "validation": validation,
                        "category": tc.get("category"),
                        "difficulty": tc.get("difficulty"),
                    }
                )

                time.sleep(1)

        # Show results
        click.echo("\n" + "=" * 80)
        click.echo(click.style("📊 RESULTS", fg="cyan", bold=True))
        click.echo("=" * 80)

        total = stats["total"]
        click.echo(f"\nTotal: {total}")
        click.echo(
            click.style(
                f"Correct: {stats['correct']}/{total} ({stats['correct']/total*100:.0f}%)",
                fg="green" if stats["correct"] > total / 2 else "red",
            )
        )
        click.echo(
            f"Relevant: {stats['relevant']}/{total} ({stats['relevant']/total*100:.0f}%)"
        )

        # Save report
        os.makedirs("reports", exist_ok=True)
        report_file = f"reports/aitest_{int(time.time())}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "url": url,
                    "provider": provider,
                    "website_type": website_type,
                    "statistics": stats,
                    "results": results,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        click.echo(f"\n📄 Report: {report_file}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
