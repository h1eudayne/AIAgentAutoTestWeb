# 🚀 Setup Guide - AI Agent Auto Test Web

## Quick Setup (5 phút)

### Bước 1: Clone Repository

```bash
git clone https://github.com/h1eudayne/AIAgentAutoTestWeb.git
cd AIAgentAutoTestWeb
```

### Bước 2: Chạy Setup Script

```bash
python setup.py
```

Script sẽ tự động:
- ✅ Kiểm tra Python version
- ✅ Cài đặt dependencies
- ✅ Tạo .env file
- ✅ Hỏi OpenAI API key
- ✅ Tạo folders cần thiết

**Output:**
```
🤖 AI Agent Auto Test Web - Setup
================================================================================

📋 Checking Python version...
✓ Python 3.11.0

📦 Installing dependencies...
   This may take a few minutes...
✓ Dependencies installed successfully

🔑 Setting up API keys...

📝 OpenAI API Key Setup
   Get your key at: https://platform.openai.com/api-keys

   Enter your OpenAI API key (or press Enter to skip): sk-...
✓ API key configured
✓ Created .env file

📁 Creating directories...
✓ Created 4 directories

🔍 Verifying setup...
   ✓ API key configured
   ✓ Reports directory created
   ✓ Core dependencies installed

================================================================================
🎉 Setup Complete!
================================================================================
```

### Bước 3: Test Ngay

```bash
# Test cơ bản (không cần API key)
python test_web.py --url https://example.com

# Test thông minh (cần API key)
python test_web_intelligent.py --url https://example.com
```

---

## Manual Setup (Nếu không dùng script)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup API Key

**Option A: .env File (Khuyến nghị)**

```bash
# Copy template
cp .env.example .env

# Edit .env và thêm key
nano .env  # hoặc notepad .env trên Windows
```

Nội dung `.env`:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

**Option B: Environment Variable**

```bash
# Linux/Mac
export OPENAI_API_KEY=sk-your-key-here

# Windows CMD
set OPENAI_API_KEY=sk-your-key-here

# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key-here"
```

**Option C: Command Line**

```bash
python test_web_intelligent.py --url URL --api-key sk-your-key-here
```

### 3. Create Directories

```bash
mkdir reports screenshots memory models
```

---

## Get OpenAI API Key

### Bước 1: Tạo Account

1. Truy cập: https://platform.openai.com/signup
2. Đăng ký với email hoặc Google
3. Verify email

### Bước 2: Add Payment Method

1. Go to: https://platform.openai.com/account/billing
2. Add credit card
3. Add credits ($5-10 recommended)

### Bước 3: Create API Key

1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Name: "AI Agent Testing"
4. Copy key (starts with `sk-proj-...`)
5. **Save securely** - you won't see it again!

### Bước 4: Set Usage Limits (Khuyến nghị)

1. Go to: https://platform.openai.com/account/limits
2. Set monthly limit: $10
3. Set email alerts: $5, $8

---

## Verify Setup

### Test 1: Basic Test (No API key needed)

```bash
python test_web.py --url https://example.com --test-cases basic
```

**Expected output:**
```
✓ Driver setup complete
✓ Page loaded in 0.45s
✓ Title: Example Domain
📸 Screenshot: screenshots/page_load_xxx.png
✓ PASS: page_load
Total: 1/1 tests passed (100.0%)
```

### Test 2: Intelligent Test (API key required)

```bash
python test_web_intelligent.py --url https://fe-history-mind-ai.vercel.app/
```

**Expected output:**
```
🤖 AI WEBSITE ANALYSIS
✓ Website Type: chatbot
✓ Description: AI chatbot for historical questions
✓ Confidence: 95.0%

🧪 GENERATING TEST STRATEGY
✓ Generated 5 test cases
✓ Generated 8 test questions

💬 CHATBOT TESTING
📝 Test 1/8
Question: Chiến tranh Việt Nam diễn ra khi nào?
✓ Valid (Score: 0.92)
```

---

## Troubleshooting

### Issue: "Python not found"

**Solution:**
```bash
# Check Python installation
python --version
# or
python3 --version

# Install Python 3.8+
# Windows: https://www.python.org/downloads/
# Mac: brew install python3
# Linux: sudo apt install python3
```

### Issue: "pip not found"

**Solution:**
```bash
# Install pip
python -m ensurepip --upgrade

# Or download get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

### Issue: "ChromeDriver not found"

**Solution:**
```bash
# Windows
# Download: https://chromedriver.chromium.org/
# Add to PATH or place in project folder

# Mac
brew install chromedriver

# Linux
sudo apt-get install chromium-chromedriver
```

### Issue: "API key invalid"

**Solution:**
1. Check key starts with `sk-proj-` or `sk-`
2. No extra spaces or quotes
3. Key not revoked
4. Verify at: https://platform.openai.com/api-keys

### Issue: "Rate limit exceeded"

**Solution:**
1. Wait 60 seconds
2. Check usage: https://platform.openai.com/usage
3. Upgrade plan if needed
4. Use gpt-4o-mini (cheaper)

### Issue: "Module not found"

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or install specific package
pip install openai selenium click
```

---

## Configuration Files

### .env (Not in Git)

```bash
# Your actual API key
OPENAI_API_KEY=sk-proj-xxxxx

# Optional settings
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.3
```

### .env.example (In Git)

```bash
# Template for users
OPENAI_API_KEY=your_openai_api_key_here
```

### .gitignore

```bash
# Already configured to ignore:
.env
*.pyc
__pycache__/
reports/
screenshots/
memory/
models/
```

---

## Security Best Practices

### ✅ DO

- ✅ Use .env file for API keys
- ✅ Add .env to .gitignore
- ✅ Set usage limits on OpenAI
- ✅ Rotate keys regularly
- ✅ Use environment variables in production

### ❌ DON'T

- ❌ Commit API keys to Git
- ❌ Share keys publicly
- ❌ Hardcode keys in code
- ❌ Use same key for multiple projects
- ❌ Store keys in plain text files (except .env)

---

## Project Structure After Setup

```
AIAgentAutoTestWeb/
├── .env                    # Your API key (not in Git)
├── .env.example           # Template (in Git)
├── .gitignore             # Ignores .env
├── setup.py               # Setup script
├── requirements.txt       # Dependencies
├── test_web.py           # Basic testing
├── test_web_intelligent.py # AI testing
├── agent/                 # Core logic
├── reports/              # Test reports (created)
├── screenshots/          # Screenshots (created)
├── memory/               # Memory files (created)
└── models/               # LLM models (created)
```

---

## Cost Estimation

### Using gpt-4o-mini (Recommended)

- **Setup**: Free
- **Basic tests**: Free (no API calls)
- **Intelligent test**: ~$0.02-0.05 per run
- **Monthly (100 tests)**: ~$2-5

### Using gpt-4o (More powerful)

- **Intelligent test**: ~$0.10-0.20 per run
- **Monthly (100 tests)**: ~$10-20

---

## Next Steps

1. ✅ Complete setup
2. ✅ Test with example.com
3. ✅ Test your own website
4. 📚 Read documentation:
   - `USER_GUIDE.md` - Basic testing
   - `INTELLIGENT_TESTING_GUIDE.md` - AI testing
   - `README.md` - Full docs

---

## Support

- **Issues**: https://github.com/h1eudayne/AIAgentAutoTestWeb/issues
- **Docs**: See README.md
- **OpenAI Help**: https://help.openai.com/

---

**Happy Testing! 🚀**
