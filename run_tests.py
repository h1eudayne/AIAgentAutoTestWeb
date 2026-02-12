#!/usr/bin/env python3
"""
Test Runner - Run all tests with coverage report
"""

import unittest
import sys
import os
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)


def run_tests(verbose=True):
    """Run all tests"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🧪 Running Test Suite{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📊 TEST SUMMARY{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = total - failures - errors - skipped
    
    print(f"Total tests: {total}")
    print(f"{Fore.GREEN}✓ Passed: {passed}{Style.RESET_ALL}")
    
    if failures > 0:
        print(f"{Fore.RED}✗ Failed: {failures}{Style.RESET_ALL}")
    
    if errors > 0:
        print(f"{Fore.RED}✗ Errors: {errors}{Style.RESET_ALL}")
    
    if skipped > 0:
        print(f"{Fore.YELLOW}⏭ Skipped: {skipped}{Style.RESET_ALL}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    # Print failures detail
    if failures > 0:
        print(f"\n{Fore.RED}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.RED}FAILURES{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}\n")
        
        for test, traceback in result.failures:
            print(f"{Fore.RED}✗ {test}{Style.RESET_ALL}")
            print(f"{traceback}\n")
    
    # Print errors detail
    if errors > 0:
        print(f"\n{Fore.RED}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.RED}ERRORS{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}\n")
        
        for test, traceback in result.errors:
            print(f"{Fore.RED}✗ {test}{Style.RESET_ALL}")
            print(f"{traceback}\n")
    
    print()
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


def run_specific_test(test_file):
    """Run a specific test file"""
    print(f"\n{Fore.CYAN}Running tests from: {test_file}{Style.RESET_ALL}\n")
    
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern=test_file)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


def list_tests():
    """List all available tests"""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📋 Available Tests{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    test_dir = Path('tests')
    if not test_dir.exists():
        print(f"{Fore.RED}Tests directory not found!{Style.RESET_ALL}")
        return
    
    test_files = sorted(test_dir.glob('test_*.py'))
    
    if not test_files:
        print(f"{Fore.YELLOW}No test files found{Style.RESET_ALL}")
        return
    
    for i, test_file in enumerate(test_files, 1):
        # Count tests in file
        loader = unittest.TestLoader()
        suite = loader.discover('tests', pattern=test_file.name)
        test_count = suite.countTestCases()
        
        print(f"{i}. {test_file.name} ({test_count} tests)")
    
    print()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run test suite for AI Agent Auto Test Web"
    )
    parser.add_argument(
        '--file',
        help='Run specific test file (e.g., test_memory.py)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available tests'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Run tests in quiet mode'
    )
    
    args = parser.parse_args()
    
    # Check if tests directory exists
    if not Path('tests').exists():
        print(f"{Fore.RED}Error: tests/ directory not found!{Style.RESET_ALL}")
        print(f"\nPlease ensure you're running from the project root directory.")
        return 1
    
    # List tests
    if args.list:
        list_tests()
        return 0
    
    # Run specific test file
    if args.file:
        return run_specific_test(args.file)
    
    # Run all tests
    return run_tests(verbose=not args.quiet)


if __name__ == "__main__":
    sys.exit(main())
