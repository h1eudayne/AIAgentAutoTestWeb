# 🚀 Quick Start Guide

## ✅ Trạng thái hiện tại

- ✅ Dependencies đã cài đặt
- ✅ Selenium hoạt động tốt
- ⏳ Cần download LLaMA 3 model

## 📥 Bước tiếp theo: Download Model

### Option 1: Download trực tiếp (Khuyến nghị)

1. Truy cập: https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/tree/main

2. Click vào file: **Meta-Llama-3-8B-Instruct-Q4_K_M.gguf** (~4.9GB)

3. Click nút "Download" ở góc phải

4. Sau khi download xong, copy file vào thư mục `models/`

5. Cập nhật `config/settings.py`:
   ```python
   LLAMA_MODEL_PATH = "models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
   ```

### Option 2: Download bằng PowerShell

```powershell
# Chạy lệnh này (download ~4.9GB, mất 10-30 phút)
Invoke-WebRequest -Uri "https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf" -OutFile "models\Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
```

### Option 3: Model nhỏ hơn (nếu RAM < 8GB)

```powershell
# Download Q3_K_M (~3.5GB) - Nhẹ hơn
Invoke-WebRequest -Uri "https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q3_K_M.gguf" -OutFile "models\Meta-Llama-3-8B-Instruct-Q3_K_M.gguf"
```

## 🧪 Test sau khi download

```bash
# Test với website demo
python main.py https://www.selenium.dev/selenium/web/web-form.html

# Hoặc test với website của bạn
python main.py https://fe-history-mind-ai.vercel.app/
```

## 📊 Xem kết quả

Báo cáo sẽ được lưu tại:
- Console: Hiển thị real-time với màu sắc
- File: `reports/test_report_YYYYMMDD_HHMMSS.json`

## 🔧 Nếu gặp lỗi

### Lỗi: "Model not found"

```bash
# Kiểm tra file model
dir models\

# Đảm bảo tên file trong config/settings.py khớp với file thực tế
```

### Lỗi: "Out of memory"

```python
# Mở config/settings.py và giảm context size:
LLAMA_N_CTX = 2048  # Thay vì 4096

# Hoặc dùng model nhỏ hơn (Q3_K_M)
```

### Lỗi: Chrome/ChromeDriver

```bash
# Cài đặt Chrome browser từ:
# https://www.google.com/chrome/
```

## 💡 Tips

1. **Lần đầu chạy sẽ chậm** (~30s) vì phải load model vào RAM
2. **Dùng Q4_K_M** cho balance tốt nhất
3. **Chạy headless** để tiết kiệm tài nguyên: `python main.py URL --headless`
4. **Đóng các app khác** khi chạy để đủ RAM

## 📚 Tài liệu thêm

- [DOWNLOAD_MODEL.md](DOWNLOAD_MODEL.md) - Hướng dẫn chi tiết download model
- [README.md](README.md) - Tài liệu đầy đủ
- [example_usage.py](example_usage.py) - Ví dụ sử dụng

---

**Cần hỗ trợ?** Mở issue hoặc liên hệ!
