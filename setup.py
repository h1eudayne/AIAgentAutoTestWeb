#!/usr/bin/env python3
"""
Setup Script for AI Agent Auto Test Web
Helps users configure API keys and environment
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header():
    """Print welcome header"""
    print("\n" + "=" * 80)
    print("🤖 AI Agent Auto Test Web - Setup")
    print("=" * 80)
    print()


def check_python_version():
    """Check Python version"""
    print("📋 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required!")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    print()


def install_dependencies():
    """Install required packages"""
    print("📦 Installing dependencies...")
    print("   This may take a few minutes...")
    print()

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install dependencies")
        print(f"   Error: {e}")
        sys.exit(1)
    print()


def setup_env_file():
    """Setup .env file"""
    print("🔑 Setting up API keys...")
    print()

    env_file = Path(".env")
    env_example = Path(".env.example")

    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("   Overwrite? (y/N): ").strip().lower()
        if response != "y":
            print("   Skipping .env setup")
            print()
            return

    # Copy from example
    if env_example.exists():
        with open(env_example, "r") as f:
            content = f.read()
    else:
        content = "OPENAI_API_KEY=your_openai_api_key_here\n"

    # Ask for API key
    print("📝 OpenAI API Key Setup")
    print("   Get your key at: https://platform.openai.com/api-keys")
    print()

    api_key = input("   Enter your OpenAI API key (or press Enter to skip): ").strip()

    if api_key:
        content = content.replace("your_openai_api_key_here", api_key)
        print("✓ API key configured")
    else:
        print("⚠️  API key not set - you'll need to set it later")

    # Write .env file
    with open(env_file, "w") as f:
        f.write(content)

    print(f"✓ Created .env file")
    print()


def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")

    dirs = ["reports", "screenshots", "memory", "models"]

    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)

    print(f"✓ Created {len(dirs)} directories")
    print()


def verify_setup():
    """Verify setup is complete"""
    print("🔍 Verifying setup...")
    print()

    checks = []

    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            content = f.read()
            if "your_openai_api_key_here" not in content:
                checks.append(("✓", "API key configured"))
            else:
                checks.append(("⚠️", "API key not set (optional)"))
    else:
        checks.append(("⚠️", ".env file not found (optional)"))

    # Check directories
    if Path("reports").exists():
        checks.append(("✓", "Reports directory created"))

    # Check dependencies
    try:
        import selenium
        import openai
        import click

        checks.append(("✓", "Core dependencies installed"))
    except ImportError:
        checks.append(("❌", "Some dependencies missing"))

    # Print results
    for status, message in checks:
        print(f"   {status} {message}")

    print()


def print_next_steps():
    """Print next steps"""
    print("=" * 80)
    print("🎉 Setup Complete!")
    print("=" * 80)
    print()
    print("📚 Next Steps:")
    print()
    print("1. Set your OpenAI API key (if not done):")
    print("   • Edit .env file and add your key")
    print("   • Or set environment variable: export OPENAI_API_KEY=your_key")
    print()
    print("2. Run basic test:")
    print("   python test_web.py --url https://example.com")
    print()
    print("3. Run intelligent test (requires API key):")
    print("   python test_web_intelligent.py --url https://example.com")
    print()
    print("4. Read documentation:")
    print("   • USER_GUIDE.md - Basic testing guide")
    print("   • INTELLIGENT_TESTING_GUIDE.md - AI-powered testing")
    print("   • README.md - Full documentation")
    print()
    print("=" * 80)
    print()


def main():
    """Main setup function"""
    print_header()

    try:
        check_python_version()
        install_dependencies()
        setup_env_file()
        create_directories()
        verify_setup()
        print_next_steps()

    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
