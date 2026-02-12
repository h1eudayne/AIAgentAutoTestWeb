# 📥 Hướng dẫn Download LLaMA 3 Model

## Cách 1: Download từ HuggingFace (Khuyến nghị)

### Bước 1: Truy cập HuggingFace

Mở link: https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/tree/main

### Bước 2: Chọn file phù hợp

Chọn một trong các file sau (theo RAM của bạn):

| File | Size | RAM cần | Chất lượng | Link |
|------|------|---------|------------|------|
| Meta-Llama-3-8B-Instruct-Q4_K_M.gguf | ~4.9GB | 8GB | ⭐ Khuyến nghị | [Download](https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf) |
| Meta-Llama-3-8B-Instruct-Q5_K_M.gguf | ~5.7GB | 10GB | Cao | [Download](https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q5_K_M.gguf) |
| Meta-Llama-3-8B-Instruct-Q3_K_M.gguf | ~3.5GB | 6GB | Thấp hơn | [Download](https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q3_K_M.gguf) |

### Bước 3: Download và đặt vào thư mục models

```bash
# Sau khi download xong, copy file vào thư mục models/
# Ví dụ:
# D:\AIAgentAutoTestWeb\models\Meta-Llama-3-8B-Instruct-Q4_K_M.gguf
```

### Bước 4: Cập nhật config

Mở file `config/settings.py` và sửa dòng:

```python
LLAMA_MODEL_PATH = "models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
```

## Cách 2: Download bằng Command Line

### Windows (PowerShell):

```powershell
# Download Q4_K_M (khuyến nghị)
Invoke-WebRequest -Uri "https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf" -OutFile "models\Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
```

### Linux/Mac:

```bash
# Download Q4_K_M (khuyến nghị)
wget -P models/ https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf
```

## Cách 3: Dùng Ollama (Dễ nhất)

```bash
# 1. Cài Ollama từ https://ollama.ai/download

# 2. Pull model
ollama pull llama3

# 3. Model sẽ được lưu tại:
# Windows: C:\Users\<username>\.ollama\models\
# Linux/Mac: ~/.ollama/models/

# 4. Copy file .gguf từ thư mục đó vào models/
```

## Kiểm tra sau khi download

```bash
# Kiểm tra file đã tồn tại
dir models\

# Chạy test
python main.py https://example.com
```

## Lỗi thường gặp

### Lỗi: "Model not found"

```bash
# Kiểm tra đường dẫn
dir models\

# Đảm bảo tên file trong config/settings.py khớp với file thực tế
```

### Lỗi: "Out of memory"

```python
# Dùng model nhỏ hơn (Q3_K_M hoặc Q4_K_M)
# Hoặc giảm context size trong config/settings.py:
LLAMA_N_CTX = 2048  # Thay vì 4096
```

---

**Lưu ý**: File model rất lớn (~3-6GB), download có thể mất 10-30 phút tùy tốc độ mạng.
