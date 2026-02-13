"""
Setup script to install aitest as a global command
"""

from setuptools import find_packages, setup

setup(
    name="aitest",
    version="1.0.0",
    description="AI-powered web testing CLI tool",
    author="Your Name",
    packages=find_packages(),
    py_modules=["aitest"],
    install_requires=[
        "selenium>=4.16.0",
        "webdriver-manager>=4.0.1",
        "colorama>=0.4.6",
        "python-dotenv>=1.0.0",
        "click>=8.0.0",
        "questionary>=2.0.0",
        "cerebras-cloud-sdk>=1.0.0",
        "google-genai>=0.2.0",
    ],
    entry_points={
        "console_scripts": [
            "aitest=aitest:main",
        ],
    },
    python_requires=">=3.8",
)
