#!/usr/bin/env python3
"""
Generate and serve Allure reports
"""

import subprocess
import sys
import os
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)


def check_allure_installed():
    """Check if Allure CLI is installed"""
    try:
        result = subprocess.run(
            ["allure", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_allure_instructions():
    """Print instructions for installing Allure CLI"""
    print(f"\n{Fore.RED}❌ Allure CLI not found!{Style.RESET_ALL}\n")
    print(f"{Fore.YELLOW}Please install Allure CLI:{Style.RESET_ALL}\n")
    
    print(f"{Fore.CYAN}Windows (Scoop):{Style.RESET_ALL}")
    print("  scoop install allure\n")
    
    print(f"{Fore.CYAN}macOS (Homebrew):{Style.RESET_ALL}")
    print("  brew install allure\n")
    
    print(f"{Fore.CYAN}Linux (Manual):{Style.RESET_ALL}")
    print("  wget https://github.com/allure-framework/allure2/releases/download/2.24.1/allure-2.24.1.tgz")
    print("  tar -zxvf allure-2.24.1.tgz")
    print("  sudo mv allure-2.24.1 /opt/allure")
    print("  sudo ln -s /opt/allure/bin/allure /usr/bin/allure\n")
    
    print(f"{Fore.CYAN}Or download from:{Style.RESET_ALL}")
    print("  https://github.com/allure-framework/allure2/releases\n")


def run_tests():
    """Run tests with Allure results"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🧪 Running Tests with Allure{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    # Clean old results
    results_dir = Path("allure-results")
    if results_dir.exists():
        import shutil
        shutil.rmtree(results_dir)
        print(f"{Fore.YELLOW}✓ Cleaned old Allure results{Style.RESET_ALL}")
    
    # Run tests
    cmd = [
        "pytest",
        "-n", "auto",
        "--dist", "loadscope",
        "--alluredir=allure-results",
        "tests/",
        "-v"
    ]
    
    print(f"{Fore.GREEN}Running: {' '.join(cmd)}{Style.RESET_ALL}\n")
    
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print(f"\n{Fore.RED}❌ Tests failed!{Style.RESET_ALL}")
        return False
    
    print(f"\n{Fore.GREEN}✓ Tests completed successfully{Style.RESET_ALL}")
    return True


def generate_report():
    """Generate Allure HTML report"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📊 Generating Allure Report{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    # Check if results exist
    results_dir = Path("allure-results")
    if not results_dir.exists() or not list(results_dir.glob("*")):
        print(f"{Fore.RED}❌ No Allure results found!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Run tests first with: pytest --alluredir=allure-results{Style.RESET_ALL}")
        return False
    
    # Generate report
    report_dir = Path("allure-report")
    
    cmd = [
        "allure",
        "generate",
        "allure-results",
        "-o", "allure-report",
        "--clean"
    ]
    
    print(f"{Fore.GREEN}Generating report...{Style.RESET_ALL}")
    
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print(f"\n{Fore.RED}❌ Failed to generate report!{Style.RESET_ALL}")
        return False
    
    print(f"\n{Fore.GREEN}✓ Report generated: {report_dir.absolute()}{Style.RESET_ALL}")
    return True


def serve_report():
    """Serve Allure report"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🌐 Serving Allure Report{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    # Check if report exists
    report_dir = Path("allure-report")
    if not report_dir.exists():
        print(f"{Fore.RED}❌ No report found!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Generate report first with: allure generate{Style.RESET_ALL}")
        return False
    
    print(f"{Fore.GREEN}Starting Allure server...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Press Ctrl+C to stop{Style.RESET_ALL}\n")
    
    cmd = ["allure", "serve", "allure-results"]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Server stopped{Style.RESET_ALL}")
    
    return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate and serve Allure reports"
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run tests before generating report'
    )
    parser.add_argument(
        '--generate',
        action='store_true',
        help='Generate report only (no serve)'
    )
    parser.add_argument(
        '--serve',
        action='store_true',
        help='Serve existing report'
    )
    
    args = parser.parse_args()
    
    # Check if Allure is installed
    if not check_allure_installed():
        install_allure_instructions()
        return 1
    
    # Default: run tests and serve
    if not any([args.test, args.generate, args.serve]):
        args.test = True
        args.serve = True
    
    # Run tests
    if args.test:
        if not run_tests():
            return 1
    
    # Generate report
    if args.generate or args.serve:
        if not generate_report():
            return 1
    
    # Serve report
    if args.serve:
        serve_report()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
