# 🤖 Intelligent Web Testing Guide

## Tổng Quan

AI Agent tự động:
- ✅ **Phát hiện loại website** (chatbot, e-commerce, blog, form...)
- ✅ **Sinh test cases phù hợp** với từng loại website
- ✅ **Tự động tạo câu hỏi** cho chatbot dựa trên domain
- ✅ **Đánh giá câu trả lời** của chatbot bằng AI
- ✅ **Quyết định số lượng test** cần thiết

---

## 🚀 Quick Start

### 1. Cài Đặt

```bash
# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY=your_api_key_here
```

### 2. Chạy Test

```bash
# Test bất kỳ website nào
python test_web_intelligent.py --url https://example.com

# Test chatbot
python test_web_intelligent.py --url https://fe-history-mind-ai.vercel.app/

# Visible browser
python test_web_intelligent.py --url https://example.com --no-headless

# Custom API key
python test_web_intelligent.py --url https://example.com --api-key YOUR_KEY
```

---

## 🎯 Cách Hoạt Động

### Bước 1: Phân Tích Website

AI phân tích HTML và xác định:
- **Loại website**: chatbot, e-commerce, blog, portfolio, form, dashboard...
- **Mô tả**: Website làm gì
- **Tính năng chính**: Các chức năng quan trọng
- **Tương tác chính**: User có thể làm gì

**Ví dụ Output:**
```
✓ Website Type: chatbot
✓ Description: AI chatbot for historical questions
✓ Confidence: 95.0%

📋 Key Features:
   • Conversational interface
   • Text input and response
   • Historical knowledge base
```

### Bước 2: Sinh Test Strategy

AI tự động tạo:
- **Test cases**: Các test cần chạy
- **Test questions**: Câu hỏi cho chatbot (nếu là chatbot)
- **Validation rules**: Quy tắc kiểm tra

**Ví dụ cho Chatbot:**
```
✓ Generated 5 test cases
✓ Generated 8 test questions

Test Questions:
  1. Chiến tranh Việt Nam diễn ra khi nào?
     Expected: 1955, 1975, Việt Nam
  
  2. Ai là người sáng lập nhà nước Việt Nam?
     Expected: Hồ Chí Minh, 1945
  
  3. Triều đại nào thống nhất Việt Nam?
     Expected: Lê Lợi, Lê dynasty
```

### Bước 3: Thực Thi Tests

**Cho Chatbot:**
- Tự động gửi từng câu hỏi
- Đợi response
- AI đánh giá response:
  - Có chứa keywords mong đợi?
  - Có relevant với câu hỏi?
  - Có helpful không?
  - Score: 0.0-1.0

**Ví dụ Output:**
```
📝 Test 1/8
Question: Chiến tranh Việt Nam diễn ra khi nào?
⏳ Waiting for response...
Response: Chiến tranh Việt Nam diễn ra từ năm 1955 đến 1975...

✓ Valid (Score: 0.92)
Feedback: Response contains all expected keywords and is highly relevant
```

### Bước 4: Report

```
📊 TEST REPORT
================================================================================
Total Tests: 8
Passed: 7
Failed: 1
Pass Rate: 87.5%

📄 Report saved: reports/intelligent_test_1234567890.json
```

---

## 🎓 Ví Dụ Thực Tế

### Example 1: Test Chatbot Lịch Sử

```bash
python test_web_intelligent.py --url https://fe-history-mind-ai.vercel.app/
```

**AI sẽ:**
1. Phát hiện: "Đây là chatbot về lịch sử Việt Nam"
2. Sinh câu hỏi:
   - "Chiến tranh Việt Nam diễn ra khi nào?"
   - "Ai là vua đầu tiên của nhà Lý?"
   - "Cuộc kháng chiến chống Pháp kéo dài bao lâu?"
3. Test từng câu và đánh giá response
4. Report: 8/10 tests passed (80%)

### Example 2: Test E-commerce Site

```bash
python test_web_intelligent.py --url https://amazon.com
```

**AI sẽ:**
1. Phát hiện: "E-commerce site with product listings"
2. Sinh test cases:
   - Test product search
   - Test add to cart
   - Test checkout flow
   - Validate product prices
3. Chạy automated tests
4. Report kết quả

### Example 3: Test Blog/News Site

```bash
python test_web_intelligent.py --url https://medium.com
```

**AI sẽ:**
1. Phát hiện: "Blog platform with articles"
2. Sinh test cases:
   - Test article loading
   - Test navigation
   - Test search functionality
   - Validate content structure
3. Chạy tests
4. Report

---

## 🔧 Configuration

### API Key

**Option 1: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY=sk-...
python test_web_intelligent.py --url https://example.com
```

**Option 2: Command Line**
```bash
python test_web_intelligent.py --url https://example.com --api-key sk-...
```

**Option 3: .env File**
```bash
# Create .env file
echo "OPENAI_API_KEY=sk-..." > .env

# Run test
python test_web_intelligent.py --url https://example.com
```

### Get API Key

1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Copy and save securely

**Cost:** ~$0.01-0.05 per test run (using gpt-4o-mini)

---

## 📊 Output Files

### JSON Report

`reports/intelligent_test_<timestamp>.json`:

```json
{
  "url": "https://example.com",
  "timestamp": "2026-02-13T14:30:00",
  "analysis": {
    "website_type": "chatbot",
    "description": "AI chatbot for historical questions",
    "key_features": ["Conversational interface", "Text input"],
    "confidence": 0.95
  },
  "test_strategy": {
    "test_questions": [
      {
        "question": "Chiến tranh Việt Nam diễn ra khi nào?",
        "expected_keywords": ["1955", "1975", "Việt Nam"],
        "validation_type": "contains"
      }
    ],
    "recommended_test_count": 8
  },
  "results": [
    {
      "test_id": "chatbot_1",
      "question": "...",
      "response": "...",
      "validation": {
        "is_valid": true,
        "score": 0.92,
        "feedback": "Response is relevant and helpful"
      }
    }
  ]
}
```

---

## 🎯 Supported Website Types

| Type | Auto-Detection | Test Generation | Example |
|------|----------------|-----------------|---------|
| **Chatbot** | ✅ | ✅ Domain-specific questions | History chatbot, Customer support |
| **E-commerce** | ✅ | ✅ Product, cart, checkout tests | Amazon, Shopify |
| **Blog/News** | ✅ | ✅ Article, navigation tests | Medium, CNN |
| **Form** | ✅ | ✅ Validation, submission tests | Contact forms, Surveys |
| **Portfolio** | ✅ | ✅ Content, navigation tests | Personal sites |
| **Dashboard** | ✅ | ✅ Data, interaction tests | Admin panels |
| **Landing Page** | ✅ | ✅ CTA, conversion tests | Marketing pages |
| **Documentation** | ✅ | ✅ Search, navigation tests | API docs |

---

## 💡 Best Practices

### 1. Chatbot Testing

```bash
# Test với nhiều câu hỏi
python test_web_intelligent.py --url https://chatbot.com

# AI sẽ tự động:
# - Phát hiện domain (history, customer support, tech...)
# - Sinh 5-10 câu hỏi relevant
# - Test conversation flow
# - Đánh giá response quality
```

### 2. E-commerce Testing

```bash
# AI sẽ test:
# - Product search
# - Add to cart
# - Checkout flow
# - Price validation
```

### 3. Form Testing

```bash
# AI sẽ test:
# - Required fields
# - Validation rules
# - Error messages
# - Submission flow
```

---

## 🔍 Troubleshooting

### Issue: "API key required"

**Solution:**
```bash
export OPENAI_API_KEY=your_key
# Or
python test_web_intelligent.py --url URL --api-key YOUR_KEY
```

### Issue: "Rate limit exceeded"

**Solution:**
- Wait a few seconds
- Use gpt-4o-mini (cheaper, faster)
- Check your OpenAI usage limits

### Issue: "Analysis failed"

**Solution:**
- Check internet connection
- Verify API key is valid
- Try with --no-headless to see browser

---

## 📈 Comparison

### Traditional Testing vs Intelligent Testing

| Feature | Traditional | Intelligent |
|---------|-------------|-------------|
| **Test Creation** | Manual | ✅ Auto-generated |
| **Website Detection** | Manual | ✅ AI-powered |
| **Test Questions** | Hardcoded | ✅ Domain-specific |
| **Response Validation** | Keyword match | ✅ AI evaluation |
| **Adaptability** | Fixed | ✅ Dynamic |
| **Setup Time** | Hours | Minutes |

---

## 🚀 Advanced Usage

### Custom Test Strategy

```python
from agent.website_analyzer import WebsiteAnalyzer

analyzer = WebsiteAnalyzer()

# Analyze
analysis = analyzer.analyze_website(html_content, url)

# Generate tests
strategy = analyzer.generate_test_cases(analysis)

# Validate response
validation = analyzer.validate_response(
    question="What is AI?",
    response="AI is artificial intelligence...",
    expected_keywords=["artificial", "intelligence"]
)
```

### Batch Testing

```bash
# Test multiple sites
for url in https://site1.com https://site2.com https://site3.com
do
  python test_web_intelligent.py --url $url
done
```

### CI/CD Integration

```yaml
# .github/workflows/intelligent-test.yml
- name: Intelligent Web Test
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    python test_web_intelligent.py --url ${{ secrets.TEST_URL }}
```

---

## 💰 Cost Estimation

Using gpt-4o-mini:
- **Website Analysis**: ~$0.01
- **Test Generation**: ~$0.01
- **Response Validation** (per question): ~$0.005

**Total per test run**: ~$0.02-0.05

**Monthly (100 tests)**: ~$2-5

---

## 🎉 Success Stories

### Chatbot Testing
- ✅ Tự động phát hiện chatbot lịch sử
- ✅ Sinh 8 câu hỏi relevant
- ✅ 87.5% pass rate
- ✅ Tiết kiệm 2 giờ manual testing

### E-commerce Testing
- ✅ Phát hiện product catalog
- ✅ Test search, cart, checkout
- ✅ 100% automated
- ✅ Tiết kiệm 4 giờ manual testing

---

## 📞 Support

- **Issues**: https://github.com/h1eudayne/AIAgentAutoTestWeb/issues
- **Documentation**: See README.md
- **OpenAI Docs**: https://platform.openai.com/docs

---

**Happy Intelligent Testing! 🤖🚀**
