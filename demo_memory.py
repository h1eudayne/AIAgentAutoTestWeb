#!/usr/bin/env python3
"""
Demo State Memory System
Minh họa cách memory hoạt động
"""

from agent.memory import StateMemory
from colorama import Fore, Style, init
import json

init(autoreset=True)

def print_section(title):
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{title}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

def demo_selector_memory():
    """Demo 1: Selector Memory"""
    print_section("DEMO 1: Selector Memory")
    
    memory = StateMemory(memory_dir="demo_memory")
    url = "https://example.com/login"
    
    print(f"Testing URL: {url}\n")
    
    # Simulate successful clicks
    print(f"{Fore.GREEN}✓ Simulating successful actions...{Style.RESET_ALL}")
    
    memory.remember_successful_selector(url, "button", "#submit-btn")
    print("  1. Clicked #submit-btn → Success")
    
    memory.remember_successful_selector(url, "button", "#submit-btn")
    print("  2. Clicked #submit-btn → Success (count: 2)")
    
    memory.remember_successful_selector(url, "button", "button:nth-of-type(1)")
    print("  3. Clicked button:nth-of-type(1) → Success")
    
    memory.remember_successful_selector(url, "button", "#submit-btn")
    print("  4. Clicked #submit-btn → Success (count: 3)")
    
    # Simulate failed clicks
    print(f"\n{Fore.RED}✗ Simulating failed actions...{Style.RESET_ALL}")
    
    memory.remember_failed_selector(url, "button", "button:nth-of-type(5)", "invalid selector")
    print("  1. Clicked button:nth-of-type(5) → Failed")
    
    memory.remember_failed_selector(url, "button", "button:nth-of-type(5)", "invalid selector")
    print("  2. Clicked button:nth-of-type(5) → Failed")
    
    memory.remember_failed_selector(url, "button", "button:nth-of-type(5)", "invalid selector")
    print("  3. Clicked button:nth-of-type(5) → Failed")
    
    # Get best selectors
    print(f"\n{Fore.YELLOW}📊 Best selectors for buttons:{Style.RESET_ALL}")
    best = memory.get_best_selectors(url, "button", limit=3)
    for i, selector in enumerate(best, 1):
        print(f"  {i}. {selector}")
    
    # Check if should avoid
    print(f"\n{Fore.YELLOW}⚠️  Should avoid selectors:{Style.RESET_ALL}")
    if memory.should_avoid_selector(url, "button", "button:nth-of-type(5)"):
        print(f"  ✓ button:nth-of-type(5) - Failed 3+ times, should avoid")
    
    if not memory.should_avoid_selector(url, "button", "#submit-btn"):
        print(f"  ✓ #submit-btn - Safe to use (success_count: 3)")

def demo_test_history():
    """Demo 2: Test History"""
    print_section("DEMO 2: Test History")
    
    memory = StateMemory(memory_dir="demo_memory")
    url = "https://example.com/login"
    
    print(f"Testing URL: {url}\n")
    
    # Simulate test results
    print(f"{Fore.GREEN}Recording test results...{Style.RESET_ALL}\n")
    
    tests = [
        {"name": "Test login button", "priority": "high", "status": "passed"},
        {"name": "Test email input", "priority": "high", "status": "passed"},
        {"name": "Test password input", "priority": "high", "status": "passed"},
        {"name": "Test remember me", "priority": "low", "status": "failed"},
        {"name": "Test forgot password", "priority": "medium", "status": "passed"},
    ]
    
    for test in tests:
        memory.remember_test_result(url, test, test)
        status_icon = "✓" if test["status"] == "passed" else "✗"
        status_color = Fore.GREEN if test["status"] == "passed" else Fore.RED
        print(f"  {status_color}{status_icon}{Style.RESET_ALL} {test['name']} - {test['priority']}")
    
    # Get statistics
    print(f"\n{Fore.YELLOW}📊 Test Statistics:{Style.RESET_ALL}")
    stats = memory.get_test_statistics(url)
    print(f"  Total tests: {stats['total']}")
    print(f"  Passed: {Fore.GREEN}{stats['passed']}{Style.RESET_ALL}")
    print(f"  Failed: {Fore.RED}{stats['failed']}{Style.RESET_ALL}")
    print(f"  Pass rate: {stats['pass_rate']}")

def demo_page_patterns():
    """Demo 3: Page Patterns"""
    print_section("DEMO 3: Page Patterns & Similarity")
    
    memory = StateMemory(memory_dir="demo_memory")
    
    # Simulate page patterns
    pages = [
        {
            "url": "https://example.com/login",
            "elements": [
                {"tag": "button", "class": "btn btn-primary"},
                {"tag": "button", "class": "btn btn-secondary"},
                {"tag": "input", "class": "form-control"},
                {"tag": "input", "class": "form-control"},
                {"tag": "a", "class": "nav-link"},
            ]
        },
        {
            "url": "https://example.com/signup",
            "elements": [
                {"tag": "button", "class": "btn btn-primary"},
                {"tag": "button", "class": "btn btn-secondary"},
                {"tag": "input", "class": "form-control"},
                {"tag": "input", "class": "form-control"},
                {"tag": "input", "class": "form-control"},
                {"tag": "a", "class": "nav-link"},
            ]
        },
        {
            "url": "https://other.com/dashboard",
            "elements": [
                {"tag": "button", "class": "action-btn"},
                {"tag": "button", "class": "action-btn"},
                {"tag": "button", "class": "action-btn"},
                {"tag": "button", "class": "action-btn"},
                {"tag": "a", "class": "menu-item"},
                {"tag": "a", "class": "menu-item"},
            ]
        }
    ]
    
    print(f"{Fore.GREEN}Learning page patterns...{Style.RESET_ALL}\n")
    
    for page in pages:
        memory.learn_page_pattern(page["url"], page)
        buttons = len([e for e in page["elements"] if e["tag"] == "button"])
        inputs = len([e for e in page["elements"] if e["tag"] == "input"])
        links = len([e for e in page["elements"] if e["tag"] == "a"])
        print(f"  {page['url']}")
        print(f"    Buttons: {buttons}, Inputs: {inputs}, Links: {links}")
    
    # Find similar pages
    print(f"\n{Fore.YELLOW}🔍 Finding similar pages to login page:{Style.RESET_ALL}")
    similar = memory.get_similar_pages("https://example.com/login", limit=2)
    
    for sim in similar:
        print(f"\n  {sim['url']}")
        print(f"    Similarity: {sim['similarity']*100:.1f}%")

def demo_recommendations():
    """Demo 4: Recommendations"""
    print_section("DEMO 4: Memory Recommendations")
    
    memory = StateMemory(memory_dir="demo_memory")
    url = "https://example.com/login"
    
    print(f"Getting recommendations for: {url}\n")
    
    recommendations = memory.get_recommendations(url)
    
    # Best selectors
    if recommendations.get("best_selectors"):
        print(f"{Fore.YELLOW}🎯 Best Selectors:{Style.RESET_ALL}")
        for elem_type, selectors in recommendations["best_selectors"].items():
            print(f"  {elem_type}:")
            for selector in selectors:
                print(f"    • {selector}")
    
    # Similar pages
    if recommendations.get("similar_pages"):
        print(f"\n{Fore.YELLOW}🔗 Similar Pages:{Style.RESET_ALL}")
        for page in recommendations["similar_pages"]:
            print(f"  • {page['url']} (similarity: {page['similarity']*100:.1f}%)")
    
    # Test stats
    if recommendations.get("test_stats", {}).get("total", 0) > 0:
        stats = recommendations["test_stats"]
        print(f"\n{Fore.YELLOW}📊 Test History:{Style.RESET_ALL}")
        print(f"  Total tests: {stats['total']}")
        print(f"  Pass rate: {stats['pass_rate']}")

def demo_memory_stats():
    """Demo 5: Memory Statistics"""
    print_section("DEMO 5: Memory Statistics")
    
    memory = StateMemory(memory_dir="demo_memory")
    
    stats = memory.get_memory_stats()
    
    print(f"{Fore.YELLOW}💾 Memory Statistics:{Style.RESET_ALL}\n")
    print(f"  Pages remembered: {stats['total_pages_remembered']}")
    print(f"  Tests in history: {stats['total_tests_in_history']}")
    print(f"  Page patterns: {stats['total_page_patterns']}")
    print(f"  Memory size: {stats['memory_size_kb']:.2f} KB")

def main():
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🧠 STATE MEMORY SYSTEM DEMO{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}This demo shows how State Memory works:{Style.RESET_ALL}")
    print("  1. Selector Memory - Remember successful/failed selectors")
    print("  2. Test History - Track all test results")
    print("  3. Page Patterns - Learn page structures")
    print("  4. Recommendations - Smart suggestions")
    print("  5. Memory Statistics - Track memory usage")
    
    input(f"\n{Fore.GREEN}Press Enter to start...{Style.RESET_ALL}")
    
    # Run demos
    demo_selector_memory()
    input(f"\n{Fore.GREEN}Press Enter for next demo...{Style.RESET_ALL}")
    
    demo_test_history()
    input(f"\n{Fore.GREEN}Press Enter for next demo...{Style.RESET_ALL}")
    
    demo_page_patterns()
    input(f"\n{Fore.GREEN}Press Enter for next demo...{Style.RESET_ALL}")
    
    demo_recommendations()
    input(f"\n{Fore.GREEN}Press Enter for next demo...{Style.RESET_ALL}")
    
    demo_memory_stats()
    
    # Final summary
    print_section("SUMMARY")
    
    print(f"{Fore.GREEN}✓ State Memory Demo Completed!{Style.RESET_ALL}\n")
    print("Memory files created in: demo_memory/")
    print("  • selector_memory.json")
    print("  • test_history.json")
    print("  • page_patterns.json")
    
    print(f"\n{Fore.YELLOW}💡 Key Takeaways:{Style.RESET_ALL}")
    print("  1. Memory learns from every test")
    print("  2. Best selectors are prioritized")
    print("  3. Failed selectors are avoided")
    print("  4. Similar pages share knowledge")
    print("  5. Agent improves over time")
    
    print(f"\n{Fore.CYAN}Check HOW_STATE_MEMORY_WORKS.md for detailed explanation!{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
