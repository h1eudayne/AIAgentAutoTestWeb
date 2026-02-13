#!/usr/bin/env python3
"""
Ví dụ sử dụng AI Web Testing Agent
"""

from main import AIWebTestAgent


def test_login_page():
    """Test trang login"""
    agent = AIWebTestAgent(headless=False)
    agent.test_website("https://practicetestautomation.com/practice-test-login/")


def test_form_page():
    """Test trang form"""
    agent = AIWebTestAgent(headless=False)
    agent.test_website("https://www.selenium.dev/selenium/web/web-form.html")


def test_ecommerce():
    """Test trang e-commerce demo"""
    agent = AIWebTestAgent(headless=False)
    agent.test_website("https://www.saucedemo.com/")


if __name__ == "__main__":
    print("Chọn test case:")
    print("1. Test Login Page")
    print("2. Test Form Page")
    print("3. Test E-commerce")

    choice = input("\nNhập lựa chọn (1-3): ")

    if choice == "1":
        test_login_page()
    elif choice == "2":
        test_form_page()
    elif choice == "3":
        test_ecommerce()
    else:
        print("Lựa chọn không hợp lệ!")
