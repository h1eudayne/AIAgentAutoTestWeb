# Configuration settings
import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent.parent
REPORTS_DIR = BASE_DIR / "reports"
PROMPTS_DIR = BASE_DIR / "prompts"

# LLaMA 3 Model settings
LLAMA_MODEL_PATH = os.getenv("LLAMA_MODEL_PATH", "models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf")
LLAMA_N_CTX = 2048  # Reduced for faster inference
LLAMA_N_GPU_LAYERS = 0  # Set > 0 if using GPU
LLAMA_N_THREADS = 4  # Number of CPU threads

# Browser settings
BROWSER_HEADLESS = False
BROWSER_TIMEOUT = 30
SCREENSHOT_ON_ERROR = True

# Agent settings
MAX_RETRIES = 3
MAX_TEST_DEPTH = 5

# Create directories
REPORTS_DIR.mkdir(exist_ok=True)
