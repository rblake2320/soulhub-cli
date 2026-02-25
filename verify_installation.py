#!/usr/bin/env python3
"""
SoulHub Installation Verification Script
=========================================
Tests that SoulHub is properly installed and working.

Run this after installing SoulHub to verify everything works.

Usage:
    python verify_installation.py
"""

import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime


class Colors:
    """Terminal colors"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def print_test(name, passed, message=""):
    """Print test result"""
    if passed:
        symbol = f"{Colors.GREEN}+{Colors.RESET}"
        status = f"{Colors.GREEN}PASS{Colors.RESET}"
    else:
        symbol = f"{Colors.RED}X{Colors.RESET}"
        status = f"{Colors.RED}FAIL{Colors.RESET}"

    print(f"{symbol} [{status}] {name}")
    if message:
        print(f"    {Colors.YELLOW}{message}{Colors.RESET}")


def run_command(cmd, capture=True):
    """Run shell command"""
    try:
        if capture:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip()
        else:
            result = subprocess.run(cmd, shell=True, timeout=30)
            return result.returncode == 0, ""
    except Exception as e:
        return False, str(e)


def test_python_version():
    """Test Python version"""
    version = sys.version_info
    passed = version >= (3, 8)
    message = f"Python {version.major}.{version.minor}.{version.micro}"
    if not passed:
        message += " (need 3.8+)"
    return passed, message


def test_git_installed():
    """Test Git installation"""
    passed, output = run_command("git --version")
    return passed, output if passed else "Git not found"


def test_gh_cli_installed():
    """Test GitHub CLI installation"""
    passed, output = run_command("gh --version")
    if passed:
        return True, output.split('\n')[0]
    return False, "GitHub CLI not found"


def test_gh_auth():
    """Test GitHub CLI authentication"""
    passed, output = run_command("gh auth status")
    if passed:
        return True, "Authenticated"
    return False, "Not authenticated (run: gh auth login)"


def test_soulhub_installed():
    """Test SoulHub CLI installation"""
    passed, output = run_command("soulhub --version")
    return passed, output if passed else "SoulHub not found (run: pip install -e .)"


def test_soulhub_commands():
    """Test SoulHub commands are available"""
    commands = [
        'init', 'deploy', 'archive', 'sync',
        'catalog', 'install', 'verify', 'status'
    ]

    passed, output = run_command("soulhub --help")
    if not passed:
        return False, "SoulHub CLI not working"

    missing = []
    for cmd in commands:
        if cmd not in output:
            missing.append(cmd)

    if missing:
        return False, f"Missing commands: {', '.join(missing)}"

    return True, f"All {len(commands)} commands available"


def test_tigs_installed():
    """Test Tigs installation"""
    passed, _ = run_command("python -c 'import tigs'")
    return passed, "Tigs installed" if passed else "Tigs not found (run: pip install tigs)"


def test_project_structure():
    """Test if running in a SoulHub project"""
    cwd = Path.cwd()
    soulhub_dir = cwd / '.soulhub'
    config_file = soulhub_dir / 'config.json'

    if not soulhub_dir.exists():
        return False, "Not in a SoulHub project (run: soulhub init)"

    if not config_file.exists():
        return False, "Missing .soulhub/config.json"

    try:
        with open(config_file) as f:
            config = json.load(f)

        if 'version' not in config:
            return False, "Invalid config.json"

        return True, f"Valid project (version {config.get('version')})"
    except Exception as e:
        return False, f"Error reading config: {e}"


def test_soul_file():
    """Test soul file exists"""
    soulhub_dir = Path.cwd() / '.soulhub'
    souls_dir = soulhub_dir / 'souls'

    if not souls_dir.exists():
        return False, "No souls directory"

    soul_files = list(souls_dir.glob('*.md'))

    if not soul_files:
        return False, "No soul files found"

    return True, f"Found {len(soul_files)} soul file(s)"


def test_git_repo():
    """Test Git repository"""
    git_dir = Path.cwd() / '.git'

    if not git_dir.exists():
        return False, "Not a Git repository"

    passed, output = run_command("git status")
    return passed, "Git repository valid" if passed else "Git repository error"


def test_github_remote():
    """Test GitHub remote"""
    passed, output = run_command("git remote -v")

    if not passed:
        return False, "No git remotes"

    if 'github.com' in output:
        # Extract repo name
        lines = output.split('\n')
        if lines:
            repo = lines[0].split()[1]
            return True, f"Connected: {repo}"

    return False, "No GitHub remote found"


def test_optional_features():
    """Test optional features"""
    results = {}

    # Real-time features (v1.1.0)
    passed, _ = run_command("python -c 'import websockets'")
    results['websockets'] = passed

    passed, _ = run_command("python -c 'import redis'")
    results['redis'] = passed

    # Training features (v1.2.0)
    passed, _ = run_command("python -c 'import torch'")
    results['pytorch'] = passed

    # Multi-modal features (v1.3.0)
    passed, _ = run_command("python -c 'from PIL import Image'")
    results['pillow'] = passed

    return results


def generate_report(tests):
    """Generate test report"""
    passed = sum(1 for _, p, _ in tests if p)
    total = len(tests)
    percentage = (passed / total) * 100

    print_header("VERIFICATION REPORT")

    print(f"Tests Passed: {passed}/{total} ({percentage:.0f}%)")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Group tests
    required = [t for t in tests if not t[0].startswith('Optional')]
    optional = [t for t in tests if t[0].startswith('Optional')]

    print(f"{Colors.BOLD}Required Tests:{Colors.RESET}")
    for name, passed, msg in required:
        print_test(name, passed, msg)

    if optional:
        print(f"\n{Colors.BOLD}Optional Features:{Colors.RESET}")
        for name, passed, msg in optional:
            print_test(name, passed, msg)

    # Overall status
    print()
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}+ ALL TESTS PASSED{Colors.RESET}")
        print(f"\n{Colors.GREEN}SoulHub is fully installed and working!{Colors.RESET}")
        return True
    elif passed >= total * 0.7:
        print(f"{Colors.YELLOW}{Colors.BOLD}! PARTIAL SUCCESS{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Core features working, some optional features missing.{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}X TESTS FAILED{Colors.RESET}")
        print(f"\n{Colors.RED}Please fix failing tests and run again.{Colors.RESET}")
        return False


def main():
    """Run all verification tests"""
    print_header("SoulHub Installation Verification")

    print(f"{Colors.BLUE}Testing SoulHub installation...{Colors.RESET}\n")

    # Run tests
    tests = []

    # Core prerequisites
    passed, msg = test_python_version()
    tests.append(("Python version", passed, msg))

    passed, msg = test_git_installed()
    tests.append(("Git installed", passed, msg))

    passed, msg = test_gh_cli_installed()
    tests.append(("GitHub CLI installed", passed, msg))

    passed, msg = test_gh_auth()
    tests.append(("GitHub authenticated", passed, msg))

    # SoulHub installation
    passed, msg = test_soulhub_installed()
    tests.append(("SoulHub CLI installed", passed, msg))

    passed, msg = test_soulhub_commands()
    tests.append(("SoulHub commands available", passed, msg))

    passed, msg = test_tigs_installed()
    tests.append(("Tigs installed", passed, msg))

    # Project structure (if in project)
    passed, msg = test_project_structure()
    tests.append(("Project structure", passed, msg))

    passed, msg = test_soul_file()
    tests.append(("Soul file exists", passed, msg))

    passed, msg = test_git_repo()
    tests.append(("Git repository", passed, msg))

    passed, msg = test_github_remote()
    tests.append(("GitHub remote", passed, msg))

    # Optional features
    optional = test_optional_features()
    tests.append(("Optional: WebSockets (v1.1.0)", optional['websockets'],
                  "For real-time features" if optional['websockets'] else "Run: pip install websockets"))
    tests.append(("Optional: Redis (v1.1.0)", optional['redis'],
                  "For pub/sub" if optional['redis'] else "Run: pip install redis"))
    tests.append(("Optional: PyTorch (v1.2.0)", optional['pytorch'],
                  "For training" if optional['pytorch'] else "Run: pip install torch"))
    tests.append(("Optional: Pillow (v1.3.0)", optional['pillow'],
                  "For multi-modal" if optional['pillow'] else "Run: pip install pillow"))

    # Generate report
    success = generate_report(tests)

    # Next steps
    if success:
        print(f"\n{Colors.BOLD}Next Steps:{Colors.RESET}")
        print("1. Customize your soul: edit .soulhub/souls/*.md")
        print("2. Deploy to Cloudflare: soulhub deploy")
        print("3. Check status: soulhub status")
        print("4. Read docs: COMPLETE_SYSTEM_GUIDE.md")

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
