"""
AI-Powered Website Analyzer
Automatically detects website type and generates intelligent test cases
"""

import os
import json
from typing import Dict, List, Optional
from openai import OpenAI


class WebsiteAnalyzer:
    """Analyze website and generate intelligent test cases using GPT-4"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize analyzer with OpenAI API key

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        self.website_type = None
        self.test_strategy = None

    def analyze_website(self, html_content: str, url: str) -> Dict:
        """
        Analyze website HTML to detect type and purpose

        Args:
            html_content: HTML content of the page
            url: Website URL

        Returns:
            Dict with website_type, description, and key_features
        """
        # Truncate HTML to avoid token limits (first 8000 chars)
        html_sample = html_content[:8000]

        prompt = f"""Analyze this website and determine its type and purpose.

URL: {url}

HTML Sample:
{html_sample}

Respond in JSON format with:
{{
  "website_type": "chatbot|ecommerce|blog|portfolio|landing_page|form|dashboard|documentation|social_media|other",
  "description": "Brief description of what the website does",
  "key_features": ["feature1", "feature2", "feature3"],
  "primary_interactions": ["interaction1", "interaction2"],
  "confidence": 0.0-1.0
}}

Focus on identifying:
- Is it a chatbot/conversational interface?
- Is it an e-commerce site with products?
- Is it a blog/news site with articles?
- Is it a form-based application?
- What are the main user interactions?
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Faster and cheaper
                messages=[
                    {
                        "role": "system",
                        "content": "You are a web testing expert who analyzes websites to determine their type and purpose.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)
            self.website_type = result.get("website_type", "other")

            return result

        except Exception as e:
            print(f"⚠️ Analysis failed: {e}")
            return {
                "website_type": "other",
                "description": "Unknown",
                "key_features": [],
                "primary_interactions": [],
                "confidence": 0.0,
            }

    def generate_test_cases(self, analysis: Dict) -> Dict:
        """
        Generate intelligent test cases based on website analysis

        Args:
            analysis: Website analysis result

        Returns:
            Dict with test_cases, test_questions (for chatbots), and validation_rules
        """
        website_type = analysis.get("website_type", "other")
        description = analysis.get("description", "")
        key_features = analysis.get("key_features", [])

        prompt = f"""Generate comprehensive test cases for this website.

Website Type: {website_type}
Description: {description}
Key Features: {', '.join(key_features)}

Generate test cases in JSON format:
{{
  "test_cases": [
    {{
      "id": "test_1",
      "name": "Test name",
      "description": "What to test",
      "steps": ["step1", "step2"],
      "expected_result": "Expected outcome",
      "priority": "high|medium|low"
    }}
  ],
  "test_questions": [
    {{
      "question": "Question to ask (for chatbots)",
      "expected_keywords": ["keyword1", "keyword2"],
      "validation_type": "contains|exact|regex",
      "category": "general|specific_domain"
    }}
  ],
  "validation_rules": [
    {{
      "element": "Element to check",
      "rule": "Validation rule",
      "importance": "critical|important|nice_to_have"
    }}
  ],
  "recommended_test_count": 5
}}

For CHATBOT websites:
- Generate 5-10 relevant questions based on the chatbot's domain
- Include both general and domain-specific questions
- Specify expected keywords in responses
- Test conversation flow

For ECOMMERCE websites:
- Test product search, add to cart, checkout flow
- Validate product listings, prices, images

For BLOG/NEWS websites:
- Test article loading, navigation, search
- Validate content structure

For FORM websites:
- Test form validation, submission
- Check required fields, error messages

Be specific and actionable!
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a QA expert who creates comprehensive test cases for different types of websites.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)
            self.test_strategy = result

            return result

        except Exception as e:
            print(f"⚠️ Test generation failed: {e}")
            return {
                "test_cases": [],
                "test_questions": [],
                "validation_rules": [],
                "recommended_test_count": 3,
            }

    def validate_response(
        self, question: str, response: str, expected_keywords: List[str]
    ) -> Dict:
        """
        Validate chatbot response using AI

        Args:
            question: Question asked
            response: Chatbot response
            expected_keywords: Expected keywords in response

        Returns:
            Dict with is_valid, score, feedback
        """
        prompt = f"""Evaluate this chatbot response.

Question: {question}
Response: {response}
Expected Keywords: {', '.join(expected_keywords)}

Evaluate in JSON format:
{{
  "is_valid": true/false,
  "score": 0.0-1.0,
  "feedback": "Brief feedback on response quality",
  "contains_keywords": ["keyword1", "keyword2"],
  "missing_keywords": ["keyword3"],
  "is_relevant": true/false,
  "is_helpful": true/false
}}

Consider:
- Does response contain expected keywords?
- Is response relevant to the question?
- Is response helpful and informative?
- Is response coherent and well-structured?
"""

        try:
            response_obj = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a QA expert evaluating chatbot responses.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            result = json.loads(response_obj.choices[0].message.content)
            return result

        except Exception as e:
            print(f"⚠️ Validation failed: {e}")
            return {
                "is_valid": False,
                "score": 0.0,
                "feedback": f"Validation error: {e}",
                "contains_keywords": [],
                "missing_keywords": expected_keywords,
                "is_relevant": False,
                "is_helpful": False,
            }

    def generate_report(self, analysis: Dict, test_strategy: Dict) -> str:
        """
        Generate human-readable report

        Args:
            analysis: Website analysis
            test_strategy: Test strategy

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("🤖 AI-POWERED WEBSITE ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")

        # Website Analysis
        report.append("📊 WEBSITE ANALYSIS")
        report.append("-" * 80)
        report.append(f"Type: {analysis.get('website_type', 'Unknown')}")
        report.append(f"Description: {analysis.get('description', 'N/A')}")
        report.append(
            f"Confidence: {analysis.get('confidence', 0.0) * 100:.1f}%"
        )
        report.append("")

        # Key Features
        features = analysis.get("key_features", [])
        if features:
            report.append("Key Features:")
            for feature in features:
                report.append(f"  • {feature}")
            report.append("")

        # Primary Interactions
        interactions = analysis.get("primary_interactions", [])
        if interactions:
            report.append("Primary Interactions:")
            for interaction in interactions:
                report.append(f"  • {interaction}")
            report.append("")

        # Test Strategy
        report.append("🧪 RECOMMENDED TEST STRATEGY")
        report.append("-" * 80)
        report.append(
            f"Recommended Tests: {test_strategy.get('recommended_test_count', 0)}"
        )
        report.append("")

        # Test Cases
        test_cases = test_strategy.get("test_cases", [])
        if test_cases:
            report.append("Test Cases:")
            for i, tc in enumerate(test_cases, 1):
                report.append(f"\n  {i}. {tc.get('name', 'Unnamed')}")
                report.append(f"     Priority: {tc.get('priority', 'medium')}")
                report.append(f"     {tc.get('description', '')}")
            report.append("")

        # Test Questions (for chatbots)
        questions = test_strategy.get("test_questions", [])
        if questions:
            report.append("Test Questions (for Chatbot):")
            for i, q in enumerate(questions, 1):
                report.append(f"\n  {i}. {q.get('question', '')}")
                keywords = q.get("expected_keywords", [])
                if keywords:
                    report.append(f"     Expected: {', '.join(keywords)}")
            report.append("")

        report.append("=" * 80)

        return "\n".join(report)
