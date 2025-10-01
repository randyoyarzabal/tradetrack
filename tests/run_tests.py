#!/usr/bin/env python3
"""
Focused test runner for TradeTrack application.
Runs essential tests with practical reporting for a small CLI project.
"""
import sys
import os
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any
import argparse


class TestRunner:
    """Focused test runner for TradeTrack application."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dir = Path(__file__).parent
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def run_command(self, command: List[str], description: str) -> Dict[str, Any]:
        """Run a command and return results."""
        print(f"✓ Running {description}...")
        
        start_time = time.time()
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            end_time = time.time()
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'duration': end_time - start_time,
                'description': description
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': 'Test timed out after 2 minutes',
                'duration': 120,
                'description': description
            }
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'duration': 0,
                'description': description
            }
    
    def run_basic_tests(self) -> Dict[str, Any]:
        """Run basic functionality tests."""
        return self.run_command(
            ['python', '-m', 'pytest', 'tests/test_basic.py', '-v'],
            'Basic Tests'
        )
    
    def run_component_tests(self) -> Dict[str, Any]:
        """Run component tests."""
        return self.run_command(
            ['python', '-m', 'pytest', 'tests/', '-v', '--tb=short'],
            'Component Tests'
        )
    
    def run_all_tests(self) -> None:
        """Run all test suites."""
        self.start_time = time.time()
        
        print("🚀 TradeTrack Test Suite (Focused)")
        print("=" * 40)
        
        # Define test suites
        test_suites = [
            self.run_basic_tests,
            self.run_component_tests
        ]
        
        # Run each test suite
        for test_suite in test_suites:
            result = test_suite()
            self.results[result['description']] = result
        
        self.end_time = time.time()
        self.print_summary()
    
    def print_summary(self) -> None:
        """Print test summary."""
        print("\n" + "=" * 40)
        print("📊 Test Summary")
        print("=" * 40)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Test Suites: {total_tests}")
        print(f"✓ Passed: {passed_tests}")
        print(f"✗ Failed: {failed_tests}")
        print(f"⏱️  Total Duration: {self.end_time - self.start_time:.2f} seconds")
        
        print("\n📋 Results:")
        print("-" * 20)
        
        for description, result in self.results.items():
            status = "✓ PASS" if result['success'] else "✗ FAIL"
            duration = f"{result['duration']:.2f}s"
            print(f"{status} {description:<20} {duration}")
            
            if not result['success'] and result['stderr']:
                print(f"    Error: {result['stderr'][:100]}...")
        
        print("\n" + "=" * 40)
        
        if failed_tests == 0:
            print("🎉 All tests passed successfully!")
            sys.exit(0)
        else:
            print(f"⚠️  {failed_tests} test suite(s) failed. Check the logs above for details.")
            sys.exit(1)
    
    def run_specific_tests(self, test_pattern: str) -> None:
        """Run specific tests matching a pattern."""
        self.start_time = time.time()
        
        print(f"🔍 Running tests matching: {test_pattern}")
        print("=" * 40)
        
        result = self.run_command(
            ['python', '-m', 'pytest', 'tests/', '-k', test_pattern, '-v', '--tb=short'],
            f'Tests matching "{test_pattern}"'
        )
        
        self.end_time = time.time()
        
        if result['success']:
            print(f"✓ Tests completed successfully in {result['duration']:.2f} seconds")
        else:
            print(f"✗ Tests failed: {result['stderr']}")
            sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='TradeTrack Focused Test Runner')
    parser.add_argument('--pattern', '-k', help='Run tests matching pattern')
    parser.add_argument('--basic', action='store_true', help='Run only basic tests')
    parser.add_argument('--component', action='store_true', help='Run only component tests')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.pattern:
        runner.run_specific_tests(args.pattern)
    elif args.basic:
        result = runner.run_basic_tests()
        print("✓ Basic tests completed" if result['success'] else "✗ Basic tests failed")
    elif args.component:
        result = runner.run_component_tests()
        print("✓ Component tests completed" if result['success'] else "✗ Component tests failed")
    else:
        runner.run_all_tests()


if __name__ == '__main__':
    main()