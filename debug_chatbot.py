#!/usr/bin/env python3
"""Debug script to understand chatbot structure"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup
opts = Options()
# opts.add_argument('--headless')
driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 20)

try:
    # Load page
    print("Loading page...")
    driver.get("https://fe-history-mind-ai.vercel.app/")
    time.sleep(5)
    
    # Find all input elements
    print("\n=== Finding input elements ===")
    inputs = driver.find_elements(By.TAG_NAME, "input")
    textareas = driver.find_elements(By.TAG_NAME, "textarea")
    
    print(f"Found {len(inputs)} input elements")
    print(f"Found {len(textareas)} textarea elements")
    
    # Try to find the input field
    input_element = None
    if textareas:
        input_element = textareas[0]
        print(f"Using textarea: {input_element.get_attribute('placeholder')}")
    elif inputs:
        for inp in inputs:
            if inp.is_displayed():
                input_element = inp
                print(f"Using input: {input_element.get_attribute('placeholder')}")
                break
    
    if not input_element:
        print("ERROR: Could not find input element!")
        print("\nPage source:")
        print(driver.page_source[:2000])
        exit(1)
    
    # Type a question
    question = "Ai là vua đầu tiên của Việt Nam?"
    print(f"\n=== Typing question: {question} ===")
    input_element.clear()
    input_element.send_keys(question)
    time.sleep(1)
    
    # Find and click submit button
    print("\n=== Finding submit button ===")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"Found {len(buttons)} buttons")
    
    for i, btn in enumerate(buttons):
        if btn.is_displayed():
            print(f"Button {i}: text='{btn.text}', type='{btn.get_attribute('type')}'")
    
    # Try to submit
    print("\n=== Submitting ===")
    try:
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()
        print("Clicked submit button")
    except:
        print("No submit button, trying Enter key")
        input_element.send_keys(Keys.RETURN)
    
    # Wait for response
    print("\n=== Waiting for response (10 seconds) ===")
    time.sleep(10)
    
    # Try to find response
    print("\n=== Looking for response ===")
    
    # Method 1: Look for message containers
    messages = driver.find_elements(By.CSS_SELECTOR, "[class*='message']")
    print(f"Found {len(messages)} elements with 'message' in class")
    for i, msg in enumerate(messages[-5:]):  # Last 5 messages
        print(f"Message {i}: {msg.text[:200]}")
    
    # Method 2: Look for chat containers
    chats = driver.find_elements(By.CSS_SELECTOR, "[class*='chat']")
    print(f"\nFound {len(chats)} elements with 'chat' in class")
    for i, chat in enumerate(chats[-3:]):  # Last 3 chats
        print(f"Chat {i}: {chat.text[:200]}")
    
    # Method 3: Get all text
    print("\n=== Full page text (last 1000 chars) ===")
    body_text = driver.find_element(By.TAG_NAME, "body").text
    print(body_text[-1000:])
    
    # Keep browser open
    print("\n=== Browser will stay open for 30 seconds ===")
    time.sleep(30)
    
finally:
    driver.quit()
