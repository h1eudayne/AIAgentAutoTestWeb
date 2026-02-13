#!/usr/bin/env python3
"""
Demo thực tế: Chạy test nhiều lần để thấy memory cải thiện
"""

import subprocess
import time

from colorama import Fore, Style, init

init(autoreset=True)


def run_test(url, run_number):
    """Chạy một lần test"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🔄 RUN #{run_number} - Testing with Memory{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    # Chạy main_fast.py với memory enabled
    result = subprocess.run(
        ["python", "main_fast.py", url], capture_output=False, text=True
    )

    time.sleep(2)
    return result.returncode == 0


def main():
    print(f"\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}🧠 STATE MEMORY DEMO - Chạy test nhiều lần{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}\n")

    print("Demo này sẽ:")
    print("  1. Chạy test 3 lần trên cùng một website")
    print("  2. Mỗi lần chạy, memory sẽ học từ lần trước")
    print("  3. Bạn sẽ thấy agent ngày càng thông minh hơn")
    print()
    print(f"{Fore.GREEN}Lưu ý: Memory được lưu trong folder memory/{Style.RESET_ALL}")
    print()

    # URL để test
    url = "https://fe-history-mind-ai.vercel.app/"

    input(f"{Fore.GREEN}Press Enter để bắt đầu...{Style.RESET_ALL}")

    # Chạy 3 lần
    for i in range(1, 4):
        success = run_test(url, i)

        if i < 3:
            print(
                f"\n{Fore.YELLOW}⏳ Đợi 3 giây trước khi chạy lần tiếp theo...{Style.RESET_ALL}"
            )
            time.sleep(3)

    # Kết luận
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}✅ HOÀN THÀNH - Đã chạy 3 lần test{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    print(f"{Fore.GREEN}💡 Những gì đã xảy ra:{Style.RESET_ALL}")
    print("  • Lần 1: Agent test và ghi nhớ selectors thành công/thất bại")
    print("  • Lần 2: Agent ưu tiên dùng selectors đã thành công từ lần 1")
    print("  • Lần 3: Agent tránh selectors đã fail, dùng best selectors")
    print()
    print(f"{Fore.YELLOW}📁 Kiểm tra memory files:{Style.RESET_ALL}")
    print("  • memory/selector_memory.json - Selectors đã học")
    print("  • memory/test_history.json - Lịch sử test")
    print("  • memory/page_patterns.json - Patterns của page")
    print()
    print(
        f"{Fore.CYAN}🎯 Kết quả: Pass rate sẽ tăng dần qua mỗi lần chạy!{Style.RESET_ALL}\n"
    )


if __name__ == "__main__":
    main()
