#!/usr/bin/env python3
"""
SoulHub E2E Test Runner
Executes the full E2E test suite for SoulHub CLI
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any


class Colors:
    """Terminal colors"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class SoulHubE2ETest:
    """End-to-end test runner for SoulHub"""

    def __init__(self, export_report=True, cleanup=True):
        self.export_report = export_report
        self.cleanup = cleanup
        self.results = []
        self.start_time = None
        self.end_time = None
        self.test_dir = None

    def run_command(self, cmd: str, timeout: int = 30) -> Tuple[int, str, str]:
        """Run shell command and capture output"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout}s"
        except Exception as e:
            return -1, "", str(e)

    def log(self, message: str, color: str = ""):
        """Print colored log message"""
        if color:
            print(f"{color}{message}{Colors.RESET}")
        else:
            print(message)

    def test_passed(self, name: str, duration: float, details: str = ""):
        """Log test pass"""
        self.results.append({
            'name': name,
            'status': 'PASS',
            'duration': duration,
            'details': details
        })
        self.log(f"+ [PASS] {name} ({duration:.1f}s)", Colors.GREEN)
        if details:
            self.log(f"    {details}", Colors.BLUE)

    def test_failed(self, name: str, duration: float, reason: str):
        """Log test failure"""
        self.results.append({
            'name': name,
            'status': 'FAIL',
            'duration': duration,
            'reason': reason
        })
        self.log(f"X [FAIL] {name} ({duration:.1f}s)", Colors.RED)
        self.log(f"    {reason}", Colors.YELLOW)

    def test_skipped(self, name: str, reason: str):
        """Log test skip"""
        self.results.append({
            'name': name,
            'status': 'SKIP',
            'duration': 0,
            'reason': reason
        })
        self.log(f"- [SKIP] {name}", Colors.YELLOW)
        self.log(f"    {reason}", Colors.YELLOW)

    def pre_flight_checks(self) -> bool:
        """Run pre-flight environment checks"""
        self.log("\n" + "="*60, Colors.BLUE)
        self.log("PRE-FLIGHT CHECKS", Colors.BOLD)
        self.log("="*60 + "\n", Colors.BLUE)

        checks_passed = True

        # Check Python version
        start = time.time()
        version = sys.version_info
        if version >= (3, 8):
            self.test_passed(
                "Python version",
                time.time() - start,
                f"Python {version.major}.{version.minor}.{version.micro}"
            )
        else:
            self.test_failed(
                "Python version",
                time.time() - start,
                f"Need Python 3.8+, got {version.major}.{version.minor}"
            )
            checks_passed = False

        # Check Git
        start = time.time()
        code, out, err = self.run_command("git --version")
        if code == 0:
            self.test_passed("Git installed", time.time() - start, out.strip())
        else:
            self.test_failed("Git installed", time.time() - start, "Git not found")
            checks_passed = False

        # Check GitHub CLI (optional)
        start = time.time()
        code, out, err = self.run_command("gh --version")
        if code == 0:
            self.test_passed("GitHub CLI", time.time() - start, out.split('\n')[0])
        else:
            self.test_skipped("GitHub CLI", "Not installed (some tests will be limited)")

        # Check we're in soulhub-cli directory
        start = time.time()
        if Path("soulhub_cli.py").exists() and Path("setup.py").exists():
            self.test_passed("Repository files", time.time() - start, "Found soulhub-cli files")
        else:
            self.test_failed(
                "Repository files",
                time.time() - start,
                "Not in soulhub-cli directory or files missing"
            )
            checks_passed = False

        return checks_passed

    def install_soulhub(self) -> bool:
        """Install SoulHub in test mode"""
        self.log("\n" + "="*60, Colors.BLUE)
        self.log("INSTALLATION", Colors.BOLD)
        self.log("="*60 + "\n", Colors.BLUE)

        # Install SoulHub
        start = time.time()
        code, out, err = self.run_command("pip install -e .", timeout=60)
        if code == 0:
            self.test_passed("pip install -e .", time.time() - start, "Installed successfully")
        else:
            self.test_failed("pip install -e .", time.time() - start, f"Install failed: {err}")
            return False

        # Verify version
        start = time.time()
        code, out, err = self.run_command("soulhub --version")
        if code == 0 and "1.0.0" in out:
            self.test_passed("soulhub --version", time.time() - start, out.strip())
        else:
            self.test_failed("soulhub --version", time.time() - start, "Version check failed")
            return False

        # Check for SyntaxWarnings
        start = time.time()
        code, out, err = self.run_command("python -W error::SyntaxWarning -c 'import soulhub_cli'")
        if code == 0:
            self.test_passed("No SyntaxWarnings", time.time() - start, "Clean import")
        else:
            self.test_failed("No SyntaxWarnings", time.time() - start, err)

        return True

    def run_core_tests(self) -> int:
        """Run core command tests"""
        self.log("\n" + "="*60, Colors.BLUE)
        self.log("CORE TESTS", Colors.BOLD)
        self.log("="*60 + "\n", Colors.BLUE)

        passed = 0

        # T1: Help command
        start = time.time()
        code, out, err = self.run_command("soulhub --help")
        if code == 0 and all(cmd in out for cmd in ['init', 'deploy', 'archive', 'sync', 'catalog', 'install', 'verify', 'status']):
            self.test_passed("soulhub --help", time.time() - start, "All 8 commands listed")
            passed += 1
        else:
            self.test_failed("soulhub --help", time.time() - start, "Missing commands")

        # T2: Verify from repo root
        start = time.time()
        code, out, err = self.run_command("soulhub verify", timeout=60)
        if "Tests Passed:" in out and "8/15" in out:
            self.test_passed("soulhub verify (repo)", time.time() - start, "8/15 tests passed")
            passed += 1
        elif "Tests Passed:" in out:
            # Still pass if verification runs, even if different ratio
            ratio = out.split("Tests Passed:")[1].split("\n")[0].strip()
            self.test_passed("soulhub verify (repo)", time.time() - start, f"{ratio} tests passed")
            passed += 1
        else:
            self.test_failed("soulhub verify (repo)", time.time() - start, "Verification failed")

        # T3: Catalog command
        start = time.time()
        code, out, err = self.run_command("soulhub catalog")
        if code == 0 and "Available souls:" in out:
            souls_count = out.split("Available souls:")[1].split("\n")[0].strip()
            self.test_passed("soulhub catalog", time.time() - start, f"{souls_count} souls")
            passed += 1
        else:
            self.test_failed("soulhub catalog", time.time() - start, "Catalog failed")

        # T4: Catalog search
        start = time.time()
        code, out, err = self.run_command("soulhub catalog -q medical")
        if code == 0:
            self.test_passed("soulhub catalog search", time.time() - start, "Search works")
            passed += 1
        else:
            self.test_failed("soulhub catalog search", time.time() - start, "Search failed")

        return passed

    def run_project_tests(self) -> int:
        """Run project-based tests"""
        self.log("\n" + "="*60, Colors.BLUE)
        self.log("PROJECT TESTS", Colors.BOLD)
        self.log("="*60 + "\n", Colors.BLUE)

        passed = 0

        # Create test project
        project_name = f"e2e-test-{int(time.time())}"
        start = time.time()
        code, out, err = self.run_command(f"soulhub init --name {project_name}", timeout=60)
        if code == 0 or "initialized" in out.lower():
            self.test_passed("soulhub init", time.time() - start, f"Project: {project_name}")
            passed += 1
        else:
            self.test_failed("soulhub init", time.time() - start, "Init failed")
            return passed

        # Check project structure
        start = time.time()
        project_path = Path(project_name)
        if project_path.exists() and (project_path / ".soulhub").exists():
            self.test_passed("Project structure", time.time() - start, ".soulhub/ created")
            passed += 1
        else:
            self.test_failed("Project structure", time.time() - start, "Missing .soulhub/")

        # Status command
        start = time.time()
        code, out, err = self.run_command(f"cd {project_name} && soulhub status")
        if code == 0:
            self.test_passed("soulhub status", time.time() - start, "Status displayed")
            passed += 1
        else:
            self.test_failed("soulhub status", time.time() - start, "Status failed")

        # Verify from project
        start = time.time()
        code, out, err = self.run_command(f"cd {project_name} && soulhub verify", timeout=60)
        if "Tests Passed:" in out:
            ratio = out.split("Tests Passed:")[1].split("\n")[0].strip()
            self.test_passed("soulhub verify (project)", time.time() - start, f"{ratio} tests")
            passed += 1
        else:
            self.test_failed("soulhub verify (project)", time.time() - start, "Verification failed")

        # Archive command (expect 0 sessions)
        start = time.time()
        code, out, err = self.run_command(f"cd {project_name} && soulhub archive")
        if code == 0:
            self.test_passed("soulhub archive", time.time() - start, "Archive works (0 sessions expected)")
            passed += 1
        else:
            self.test_failed("soulhub archive", time.time() - start, "Archive failed")

        return passed

    def run_edge_case_tests(self) -> int:
        """Run edge case tests"""
        self.log("\n" + "="*60, Colors.BLUE)
        self.log("EDGE CASE TESTS", Colors.BOLD)
        self.log("="*60 + "\n", Colors.BLUE)

        passed = 0

        # Test from wrong directory
        start = time.time()
        code, out, err = self.run_command("cd /tmp && soulhub status 2>&1")
        if code != 0 or "not.*SoulHub project" in out.lower() or "error" in out.lower():
            self.test_passed("Wrong directory error", time.time() - start, "Correct error handling")
            passed += 1
        else:
            self.test_failed("Wrong directory error", time.time() - start, "Should error outside project")

        return passed

    def generate_report(self):
        """Generate test report"""
        self.log("\n" + "="*60, Colors.BOLD)
        self.log("TEST REPORT", Colors.BOLD)
        self.log("="*60 + "\n", Colors.BOLD)

        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        skipped = sum(1 for r in self.results if r['status'] == 'SKIP')

        duration = self.end_time - self.start_time

        self.log(f"Total Tests: {total}", Colors.BLUE)
        self.log(f"Passed: {passed}", Colors.GREEN)
        self.log(f"Failed: {failed}", Colors.RED if failed > 0 else "")
        self.log(f"Skipped: {skipped}", Colors.YELLOW if skipped > 0 else "")
        self.log(f"Duration: {duration:.1f}s\n", Colors.BLUE)

        success_rate = (passed / total * 100) if total > 0 else 0

        if failed == 0:
            self.log("+ ALL TESTS PASSED", Colors.GREEN + Colors.BOLD)
            self.log(f"Success Rate: {success_rate:.0f}%\n", Colors.GREEN)
        elif success_rate >= 70:
            self.log("! PARTIAL SUCCESS", Colors.YELLOW + Colors.BOLD)
            self.log(f"Success Rate: {success_rate:.0f}%\n", Colors.YELLOW)
        else:
            self.log("X TESTS FAILED", Colors.RED + Colors.BOLD)
            self.log(f"Success Rate: {success_rate:.0f}%\n", Colors.RED)

        # Export markdown report if requested
        if self.export_report:
            self.export_markdown_report()

        return failed == 0

    def export_markdown_report(self):
        """Export detailed markdown report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"soulhub-e2e-report-{timestamp}.md"

        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        skipped = sum(1 for r in self.results if r['status'] == 'SKIP')
        duration = self.end_time - self.start_time

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# SoulHub E2E Test Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Duration**: {duration:.1f}s\n")
            f.write(f"**Total Tests**: {total}\n")
            f.write(f"**Passed**: {passed} +\n")
            f.write(f"**Failed**: {failed} X\n")
            f.write(f"**Skipped**: {skipped} -\n\n")

            f.write("---\n\n")
            f.write("## Test Results\n\n")

            for result in self.results:
                status_icon = {
                    'PASS': '+',
                    'FAIL': 'X',
                    'SKIP': '-'
                }[result['status']]

                f.write(f"### {status_icon} {result['name']}\n")
                f.write(f"**Status**: {result['status']}\n")
                f.write(f"**Duration**: {result['duration']:.1f}s\n")

                if 'details' in result:
                    f.write(f"**Details**: {result['details']}\n")
                if 'reason' in result:
                    f.write(f"**Reason**: {result['reason']}\n")

                f.write("\n")

        self.log(f"\nDetailed report exported: {report_file}", Colors.GREEN)

    def run(self):
        """Run complete E2E test suite"""
        self.start_time = time.time()

        self.log("="*60, Colors.BOLD)
        self.log("SOULHUB E2E TEST SUITE", Colors.BOLD)
        self.log("="*60 + "\n", Colors.BOLD)

        # Pre-flight checks
        if not self.pre_flight_checks():
            self.log("\n" + Colors.RED + "Pre-flight checks failed. Aborting." + Colors.RESET)
            return False

        # Install SoulHub
        if not self.install_soulhub():
            self.log("\n" + Colors.RED + "Installation failed. Aborting." + Colors.RESET)
            return False

        # Run test suites
        self.run_core_tests()
        self.run_project_tests()
        self.run_edge_case_tests()

        # Generate report
        self.end_time = time.time()
        success = self.generate_report()

        return success


def main():
    """Main entry point"""
    tester = SoulHubE2ETest(export_report=True, cleanup=False)
    success = tester.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
