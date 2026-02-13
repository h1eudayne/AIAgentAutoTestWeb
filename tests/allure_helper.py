"""
Allure Helper - Utilities for Allure reporting
"""

import allure
from pathlib import Path
from typing import Optional
import json


def attach_screenshot(screenshot_path: str, name: str = "Screenshot"):
    """Attach screenshot to Allure report"""
    if Path(screenshot_path).exists():
        allure.attach.file(
            screenshot_path, name=name, attachment_type=allure.attachment_type.PNG
        )


def attach_text(
    text: str, name: str = "Text", attachment_type=allure.attachment_type.TEXT
):
    """Attach text content to Allure report"""
    allure.attach(text, name=name, attachment_type=attachment_type)


def attach_json(data: dict, name: str = "JSON Data"):
    """Attach JSON data to Allure report"""
    allure.attach(
        json.dumps(data, indent=2, ensure_ascii=False),
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )


def attach_html(html: str, name: str = "HTML"):
    """Attach HTML content to Allure report"""
    allure.attach(html, name=name, attachment_type=allure.attachment_type.HTML)


def attach_file(filepath: str, name: Optional[str] = None):
    """Attach any file to Allure report"""
    path = Path(filepath)
    if path.exists():
        if name is None:
            name = path.name

        # Determine attachment type based on extension
        ext = path.suffix.lower()
        attachment_type_map = {
            ".png": allure.attachment_type.PNG,
            ".jpg": allure.attachment_type.JPG,
            ".jpeg": allure.attachment_type.JPG,
            ".json": allure.attachment_type.JSON,
            ".xml": allure.attachment_type.XML,
            ".html": allure.attachment_type.HTML,
            ".txt": allure.attachment_type.TEXT,
            ".log": allure.attachment_type.TEXT,
        }

        attachment_type = attachment_type_map.get(ext, allure.attachment_type.TEXT)

        allure.attach.file(str(path), name=name, attachment_type=attachment_type)


@allure.step("Setup test environment")
def step_setup(description: str = ""):
    """Allure step for test setup"""
    if description:
        allure.attach(description, "Setup Details", allure.attachment_type.TEXT)


@allure.step("Execute action: {action}")
def step_action(action: str, details: Optional[str] = None):
    """Allure step for test action"""
    if details:
        allure.attach(details, "Action Details", allure.attachment_type.TEXT)


@allure.step("Verify result: {expected}")
def step_verify(expected: str, actual: str):
    """Allure step for verification"""
    allure.attach(
        f"Expected: {expected}\nActual: {actual}",
        "Verification",
        allure.attachment_type.TEXT,
    )


@allure.step("Cleanup test environment")
def step_cleanup(description: str = ""):
    """Allure step for test cleanup"""
    if description:
        allure.attach(description, "Cleanup Details", allure.attachment_type.TEXT)


def add_environment_info(env_dict: dict):
    """Add environment information to Allure report"""
    env_file = Path("allure-results/environment.properties")
    env_file.parent.mkdir(parents=True, exist_ok=True)

    with open(env_file, "w") as f:
        for key, value in env_dict.items():
            f.write(f"{key}={value}\n")


def add_categories(categories: list):
    """Add test categories to Allure report"""
    categories_file = Path("allure-results/categories.json")
    categories_file.parent.mkdir(parents=True, exist_ok=True)

    with open(categories_file, "w") as f:
        json.dump(categories, f, indent=2)


# Default categories for test failures
DEFAULT_CATEGORIES = [
    {
        "name": "Selector Issues",
        "matchedStatuses": ["failed"],
        "messageRegex": ".*NoSuchElementException.*",
    },
    {
        "name": "Timeout Issues",
        "matchedStatuses": ["failed"],
        "messageRegex": ".*TimeoutException.*",
    },
    {
        "name": "Network Issues",
        "matchedStatuses": ["failed", "broken"],
        "messageRegex": ".*ConnectionError.*|.*NetworkError.*",
    },
    {
        "name": "Assertion Failures",
        "matchedStatuses": ["failed"],
        "messageRegex": ".*AssertionError.*",
    },
    {"name": "Product Defects", "matchedStatuses": ["failed"]},
    {"name": "Test Defects", "matchedStatuses": ["broken"]},
]
