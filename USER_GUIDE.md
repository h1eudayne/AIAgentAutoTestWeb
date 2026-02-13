# AI Agent Auto Test Web - User Guide

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/h1eudayne/AIAgentAutoTestWeb.git
cd AIAgentAutoTestWeb

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

Test any website with a single command:

```bash
python test_web.py --url https://example.com
```

---

## 📖 Usage Examples

### 1. Test with URL

```bash
# Basic test
python test_web.py --url https://fe-history-mind-ai.vercel.app/

# Test specific cases
python test_web.py --url https://example.com --test-cases elements

# Run with visible browser (no headless)
python test_web.py --url https://example.com --no-headless
```

### 2. Interactive Mode

```bash
python test_web.py --interactive
```

You'll be prompted for:
- URL to test
- Headless mode (yes/no)
- Timeout (seconds)
- Test cases to run

### 3. Test Cases Options

```bash
# Run all tests (default)
python test_web.py --url https://example.com --test-cases all

# Run only basic tests (page load)
python test_web.py --url https://example.com --test-cases basic

# Test UI elements
python test_web.py --url https://example.com --test-cases elements

# Test links
python test_web.py --url https://example.com --test-cases links

# Test forms
python test_web.py --url https://example.com --test-cases forms

# Test responsive design
python test_web.py --url https://example.com --test-cases responsive

# Test performance
python test_web.py --url https://example.com --test-cases performance
```

### 4. Advanced Options

```bash
# Custom timeout
python test_web.py --url https://example.com --timeout 30

# Short form options
python test_web.py -u https://example.com -tc all -t 30

# Combine options
python test_web.py -u https://example.com --no-headless -tc responsive
```

---

## 📊 Test Cases Explained

### Basic Tests
- **Page Load**: Measures load time, captures title and URL
- **Screenshot**: Saves page screenshot

### Elements Tests
- Finds common UI elements: inputs, buttons, links, forms, images
- Reports count and selectors

### Links Tests
- Checks first 5 links on page
- Validates href attributes
- Reports link text and URLs

### Forms Tests
- Finds all forms on page
- Counts inputs, textareas, and buttons in each form
- Reports form structure

### Responsive Tests
- Tests 3 viewports: mobile (375x667), tablet (768x1024), desktop (1920x1080)
- Captures screenshots for each viewport
- Validates responsive design

### Performance Tests
- Measures page load time
- Measures DOM ready time
- Uses Navigation Timing API

---

## 📁 Output Files

### Screenshots
All screenshots are saved in `screenshots/` directory:
- `page_load_<timestamp>.png` - Initial page load
- `responsive_mobile_<timestamp>.png` - Mobile viewport
- `responsive_tablet_<timestamp>.png` - Tablet viewport
- `responsive_desktop_<timestamp>.png` - Desktop viewport

### Reports
JSON reports are saved in `reports/` directory:
- `test_report_<timestamp>.json` - Complete test results

Example report structure:
```json
{
  "url": "https://example.com",
  "timestamp": "2026-02-13T14:00:22",
  "summary": {
    "total": 6,
    "passed": 6,
    "failed": 0
  },
  "results": {
    "page_load": {
      "status": "pass",
      "load_time": 0.45,
      "title": "Example Domain",
      "url": "https://example.com"
    }
  }
}
```

---

## 🎯 Real-World Examples

### Example 1: Test E-commerce Site

```bash
python test_web.py --url https://amazon.com --test-cases all
```

This will:
- ✅ Check page load time
- ✅ Find product search input
- ✅ Find "Add to Cart" buttons
- ✅ Check navigation links
- ✅ Test responsive design
- ✅ Measure performance

### Example 2: Test Blog/News Site

```bash
python test_web.py --url https://medium.com --test-cases links
```

This will:
- ✅ Find all article links
- ✅ Validate link structure
- ✅ Report broken links

### Example 3: Test Form-Heavy Site

```bash
python test_web.py --url https://forms.google.com --test-cases forms
```

This will:
- ✅ Find all forms
- ✅ Count form fields
- ✅ Identify input types

### Example 4: Test Your Own Site

```bash
# Development
python test_web.py --url http://localhost:3000 --no-headless

# Production
python test_web.py --url https://your-site.com --test-cases all
```

---

## 🔧 Troubleshooting

### Chrome Driver Issues

If you get "chromedriver not found":

```bash
# Windows
# Download from: https://chromedriver.chromium.org/
# Add to PATH or place in project directory

# Linux
sudo apt-get install chromium-chromedriver

# Mac
brew install chromedriver
```

### Timeout Issues

If tests timeout, increase timeout:

```bash
python test_web.py --url https://slow-site.com --timeout 60
```

### Headless Mode Issues

If headless mode fails, try visible mode:

```bash
python test_web.py --url https://example.com --no-headless
```

---

## 📚 Advanced Features

### Custom Test Scripts

For more complex testing, use the simple test template:

```bash
# Copy template
cp test_history_chatbot_simple.py my_custom_test.py

# Edit and customize
# Run your custom test
python my_custom_test.py
```

### CI/CD Integration

Add to your GitHub Actions:

```yaml
- name: Run Web Tests
  run: |
    python test_web.py --url ${{ secrets.TEST_URL }} --test-cases all
```

### Batch Testing

Test multiple URLs:

```bash
# Create a script
for url in https://site1.com https://site2.com https://site3.com
do
  python test_web.py --url $url --test-cases basic
done
```

---

## 🎓 Tips & Best Practices

1. **Start with basic tests** before running all tests
2. **Use --no-headless** for debugging
3. **Increase timeout** for slow sites
4. **Check screenshots** to verify visual issues
5. **Review JSON reports** for detailed analysis
6. **Run tests regularly** to catch regressions

---

## 📞 Support

- **Issues**: https://github.com/h1eudayne/AIAgentAutoTestWeb/issues
- **Documentation**: See README.md
- **Examples**: See `test_history_chatbot_simple.py`

---

## 🎉 Success Stories

### Tested Websites
- ✅ History Mind AI Chatbot - 100% pass
- ✅ E-commerce sites - Form validation
- ✅ News sites - Link checking
- ✅ SaaS apps - Responsive testing

---

**Happy Testing! 🚀**
