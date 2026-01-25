#!/usr/bin/env python3
"""
Test runner for LEGO Robot Agent test scripts.

This script runs all test scripts in the tests directory and provides
a summary of the results.

Usage:
    python run_tests.py [test_name]
    
Examples:
    python run_tests.py                    # Run all tests
    python run_tests.py test3             # Run test3_object_detection.py
    python run_tests.py object_detection  # Run test3_object_detection.py
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from typing import List, Tuple

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class TestResult:
    """Container for test execution results."""
    def __init__(self, name: str, passed: bool, output: str, error: str = None):
        self.name = name
        self.passed = passed
        self.output = output
        self.error = error

def get_test_files() -> List[Path]:
    """Get all test*.py files in the tests directory."""
    # Try multiple locations for the tests directory
    script_dir = Path(__file__).parent
    possible_paths = [
        script_dir / "tests",
        script_dir / "src" / "tests",
        Path("src/tests"),
        Path("tests")
    ]
    
    tests_dir = None
    for path in possible_paths:
        if path.exists() and path.is_dir():
            tests_dir = path
            break
    
    if tests_dir is None:
        print(f"{RED}Error: tests directory not found{RESET}")
        print(f"Searched in: {', '.join(str(p) for p in possible_paths)}")
        sys.exit(1)
    
    # Get all test files
    test_files = sorted(tests_dir.glob("test*.py"))
    
    # Filter out __init__.py and other non-test files
    test_files = [f for f in test_files if not f.name.startswith("test_") or f.name in [
        "test1_action.py",
        "test2_yolo.py", 
        "test3_object_detection.py",
        "test4_simple_sequential.py",
        "test5_multiple_agent.py"
    ]]
    
    return test_files

def run_test(test_file: Path, timeout: int = 30) -> TestResult:
    """
    Run a single test file and capture the result.
    
    Args:
        test_file: Path to the test file
        timeout: Maximum execution time in seconds
        
    Returns:
        TestResult object with test execution details
    """
    test_name = test_file.stem
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=test_file.parent
        )
        
        passed = result.returncode == 0
        output = result.stdout
        error = result.stderr if result.returncode != 0 else None
        
        return TestResult(test_name, passed, output, error)
        
    except subprocess.TimeoutExpired:
        return TestResult(
            test_name,
            False,
            "",
            f"Test exceeded {timeout}s timeout"
        )
    except Exception as e:
        return TestResult(
            test_name,
            False,
            "",
            f"Error running test: {str(e)}"
        )

def print_test_header(test_name: str):
    """Print a formatted test header."""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}Running: {test_name}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_test_result(result: TestResult, verbose: bool = False):
    """Print the result of a test execution."""
    status_icon = f"{GREEN}✓{RESET}" if result.passed else f"{RED}✗{RESET}"
    status_text = f"{GREEN}PASSED{RESET}" if result.passed else f"{RED}FAILED{RESET}"
    
    print(f"{status_icon} {BOLD}{result.name}{RESET}: {status_text}")
    
    if verbose or not result.passed:
        if result.output:
            print(f"\n{BOLD}Output:{RESET}")
            print(result.output)
        
        if result.error:
            print(f"\n{BOLD}{RED}Error:{RESET}")
            print(result.error)

def print_summary(results: List[TestResult]):
    """Print a summary of all test results."""
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}Test Summary{RESET}")
    print(f"{BOLD}{'='*70}{RESET}")
    print(f"Total Tests: {len(results)}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {failed}{RESET}")
    
    if failed > 0:
        print(f"\n{BOLD}{RED}Failed Tests:{RESET}")
        for result in results:
            if not result.passed:
                print(f"  - {result.name}")
                if result.error and len(result.error) < 200:
                    print(f"    {YELLOW}{result.error[:200]}{RESET}")

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Run LEGO Robot Agent test scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Run all tests
  %(prog)s test3             # Run test3_object_detection.py
  %(prog)s object_detection  # Run test3_object_detection.py
  %(prog)s -v                # Run all tests with verbose output
        """
    )
    parser.add_argument(
        "test",
        nargs="?",
        help="Specific test to run (name or number)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output for all tests"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=30,
        help="Timeout for each test in seconds (default: 30)"
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List available tests"
    )
    
    args = parser.parse_args()
    
    # Get all test files
    test_files = get_test_files()
    
    if not test_files:
        print(f"{RED}No test files found{RESET}")
        return 1
    
    # List tests if requested
    if args.list:
        print(f"{BOLD}Available tests:{RESET}")
        for test_file in test_files:
            print(f"  - {test_file.stem}")
        return 0
    
    # Filter tests if specific test requested
    if args.test:
        test_pattern = args.test.lower()
        test_files = [
            f for f in test_files 
            if test_pattern in f.stem.lower()
        ]
        
        if not test_files:
            print(f"{RED}No tests match pattern: {args.test}{RESET}")
            return 1
    
    # Run tests
    results = []
    
    print(f"{BOLD}Running {len(test_files)} test(s)...{RESET}")
    
    for test_file in test_files:
        print_test_header(test_file.stem)
        result = run_test(test_file, timeout=args.timeout)
        results.append(result)
        print_test_result(result, verbose=args.verbose)
    
    # Print summary
    print_summary(results)
    
    # Return exit code based on results
    return 0 if all(r.passed for r in results) else 1

if __name__ == "__main__":
    sys.exit(main())
