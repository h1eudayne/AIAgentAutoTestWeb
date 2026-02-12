# 🤖 AI Web Testing Agent

Agent tự động test web sử dụng **LLaMA 3** + **Selenium** - không cần viết test case thủ công!

## ✨ Tính năng

✅ Tự động phân tích giao diện web (DOM + text + hành vi)  
✅ Tự động suy luận chức năng (login, search, form, checkout...)  
✅ Tự động sinh test cases (normal flow + edge cases + error handling)  
✅ Tự động thực thi tests  
✅ Tự động phát hiện lỗi  
✅ Báo cáo chi tiết với khuyến nghị  

## 🏗️ Kiến trúc

```
User Goal
    ↓
🧠 LLM Reasoning Layer (LLaMA 3)
    ↓
🗺️ Planner (Test Strategy)
    ↓
🕷️ Browser Controller (Selenium)
    ↓
📊 Analyzer + Reporter
```

## 📦 Cài đặt

### Bước 1: Cài dependencies

```bash
python -m pip install -r requirements.txt
```

✅ **HOÀN THÀNH** - Dependencies đã được cài đặt!

### Bước 2: Test Selenium (không cần model)

```bash
python test_without_model.py
```

✅ **HOÀN THÀNH** - Selenium hoạt động tốt!

### Bước 3: Download LLaMA 3 Model

**Xem hướng dẫn chi tiết tại: [DOWNLOAD_MODEL.md](DOWNLOAD_MODEL.md)**

Quick download (Windows PowerShell):

```powershell
# Download model Q4_K_M (~4.9GB) - Khuyến nghị
Invoke-WebRequest -Uri "https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf" -OutFile "models\Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
```

### Bước 4: Cấu hình model path

Mở `config/settings.py` và sửa:

```python
LLAMA_MODEL_PATH = "models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
```

## 🚀 Sử dụng

### Cách 1: Command Line

```bash
# Test một website
python main.py https://example.com

# Chạy headless (không hiện browser)
python main.py https://example.com --headless

# Chỉ định model khác
python main.py https://example.com --model models/llama-3-8b.Q5_K_M.gguf
```

### Cách 2: Import vào code

```python
from main import AIWebTestAgent

agent = AIWebTestAgent(headless=False)
agent.test_website("https://example.com")
```

## 📊 Kết quả

Agent sẽ tạo báo cáo tại thư mục `reports/`:

- **Console**: Hiển thị kết quả real-time với màu sắc
- **JSON**: File báo cáo chi tiết `test_report_YYYYMMDD_HHMMSS.json`

Ví dụ output:

```
================================================================================
🤖 AI WEB TESTING AGENT - TEST REPORT
================================================================================

📍 URL: https://example.com
⏰ Time: 2026-02-12 10:30:45

📊 SUMMARY
  Total Tests: 5
  ✓ Passed: 4
  ✗ Failed: 1
  Pass Rate: 80.0%

📋 TEST RESULTS
  ✓ [HIGH] Test valid login
  ✓ [HIGH] Test empty username
  ✗ [MEDIUM] Test special characters
      → Step 3 failed: Element not found
  ✓ [LOW] Test remember me checkbox
  ✓ [MEDIUM] Test forgot password link

💡 RECOMMENDATIONS
  ⚠️ 1 element not found errors. Selectors may need updating.
```

## 🔧 Cấu trúc Project

```
ai-web-tester/
├── agent/
│   ├── planner.py        # Sinh test strategy với LLaMA 3
│   ├── executor.py       # Điều khiển Selenium
│   ├── analyzer.py       # Phân tích kết quả
│   └── reporter.py       # Tạo báo cáo
├── prompts/
│   ├── ui_analysis.txt   # Prompt phân tích UI
│   └── test_generation.txt  # Prompt sinh test cases
├── tools/
│   └── browser.py        # Browser automation
├── config/
│   └── settings.py       # Cấu hình
├── reports/              # Báo cáo test
├── requirements.txt
├── main.py              # Entry point
└── README.md
```

## ⚙️ Tùy chỉnh

### Thay đổi timeout

Trong `config/settings.py`:

```python
BROWSER_TIMEOUT = 30  # seconds
```

### Thay đổi số lượng test cases

Chỉnh sửa prompt trong `prompts/test_generation.txt`

### Sử dụng GPU

Trong `config/settings.py`:

```python
LLAMA_N_GPU_LAYERS = 35  # Số layer chạy trên GPU
```

## 🎯 Loại web hỗ trợ

| Loại web | Khả năng |
|----------|----------|
| Landing page | ✅ 100% |
| Web CRUD | ✅ 90% |
| E-commerce | ✅ 80% |
| Web có CAPTCHA | ❌ |
| Web game | ❌ |

## 🐛 Troubleshooting

### Lỗi: Model not found

```bash
# Kiểm tra đường dẫn model
ls -la models/

# Cập nhật LLAMA_MODEL_PATH trong config/settings.py
```

### Lỗi: ChromeDriver

```bash
# Cài đặt lại webdriver-manager
pip install --upgrade webdriver-manager
```

### Lỗi: Out of memory

```bash
# Dùng model nhỏ hơn (Q4_K_M thay vì Q5_K_M)
# Hoặc giảm LLAMA_N_CTX trong config/settings.py
LLAMA_N_CTX = 2048  # Thay vì 4096
```

## 📚 Tài liệu tham khảo

- [LLaMA 3 Documentation](https://github.com/meta-llama/llama3)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)

## 🔮 Roadmap

- [ ] Hỗ trợ nhiều browser (Firefox, Edge)
- [ ] Visual regression testing
- [ ] API testing integration
- [ ] CI/CD integration
- [ ] Memory system (học từ test cũ)
- [ ] Risk-based testing
- [ ] Coverage scoring

## 📝 License

MIT License

---

**Made with ❤️ using LLaMA 3 + Selenium**
