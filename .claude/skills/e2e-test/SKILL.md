# SoulHub End-to-End Testing Skill

## Overview
Comprehensive automated testing skill for SoulHub CLI - an AI memory and deployment system. Tests installation, core commands, optional features, and generates detailed validation reports.

## Skill Metadata
```yaml
name: soulhub-e2e-test
version: 1.0.0
description: End-to-end testing for SoulHub CLI with parallel research and comprehensive validation
author: SoulHub Team
requires:
  - Python 3.8+
  - Git
  - GitHub CLI (optional for full tests)
  - Claude Code environment
```

---

## Testing Phases

### Pre-flight Checks
**Purpose**: Validate environment before testing begins

**Actions**:
1. ✅ Check Python version (must be 3.8+)
2. ✅ Verify Git is installed
3. ✅ Check GitHub CLI installation (warn if missing)
4. ✅ Confirm we're in the soulhub-cli directory
5. ✅ Verify required files exist (setup.py, soulhub_cli.py, verify_installation.py)

**Failure Handling**:
- Missing Python 3.8+: ABORT with installation instructions
- Missing Git: ABORT with installation instructions
- Missing gh CLI: WARN (some tests will be skipped)
- Wrong directory: Attempt to find soulhub-cli or ABORT
- Missing files: ABORT (not a valid SoulHub repo)

---

### Phase 1: Parallel Research (3 Sub-Agents)

**Purpose**: Simultaneously investigate SoulHub structure, dependencies, and test scenarios

#### Sub-Agent 1: Repository Structure Analysis
**Task**: Map out SoulHub architecture and files

**Research**:
- Read `README.md` for overview
- Read `COMPLETE_SYSTEM_GUIDE.md` for full documentation
- Read `LLM_SETUP_PROTOCOL.md` for setup steps
- Identify all Python files and their purposes
- Map command structure from `soulhub_cli.py`
- List all available commands (init, deploy, archive, sync, catalog, install, verify, status)

**Output**:
```yaml
structure:
  core_files:
    - soulhub_cli.py (21KB - v1.0.0 base)
    - soulhub_realtime.py (14KB - v1.1.0 alpha)
    - soulhub_training.py (16KB - v1.2.0 alpha)
    - soulhub_multimodal.py (12KB - v1.3.0 alpha)
  commands:
    - init (create project)
    - deploy (push to GitHub)
    - archive (save conversations)
    - sync (coordinate agents)
    - catalog (browse souls)
    - install (install souls)
    - verify (run tests)
    - status (show config)
```

#### Sub-Agent 2: Dependencies & Requirements Analysis
**Task**: Understand dependency structure and what's needed

**Research**:
- Read `setup.py` for base dependencies
- Read `requirements.txt` for core deps
- Read `requirements-realtime.txt` for v1.1.0
- Read `requirements-training.txt` for v1.2.0
- Read `requirements-multimodal.txt` for v1.3.0
- Check which dependencies are currently installed
- Identify which optional features can be tested

**Output**:
```yaml
dependencies:
  base:
    - click (CLI framework)
    - requests (HTTP)
    - gitpython (Git operations)
    - tigs (conversation archiving)
  optional:
    v1.1.0:
      - websockets (real-time)
      - redis (pub/sub)
    v1.2.0:
      - torch (training)
      - transformers (models)
      - unsloth (LoRA)
    v1.3.0:
      - pillow (images)
      - whisper (audio)
      - clip (embeddings)
  installed: [list of what's available]
  testable_features: [what we can test]
```

#### Sub-Agent 3: Test Scenario Discovery
**Task**: Identify all test scenarios and expected behaviors

**Research**:
- Read `verify_installation.py` for existing tests
- Read `TESTING_GUIDE.md` for test procedures
- Read `BUG_FIXES_COMPLETE.md` for known issues
- Identify edge cases and failure modes
- Map out user journeys to test

**Output**:
```yaml
test_scenarios:
  installation:
    - pip install -e . (editable mode)
    - soulhub --version
    - soulhub --help

  core_commands:
    - soulhub init --name test-project
    - soulhub status
    - soulhub verify
    - soulhub catalog
    - soulhub archive

  optional_features:
    - soulhub serve (if websockets installed)
    - soulhub connect (if websockets installed)
    - soulhub train (if torch installed)
    - soulhub remember-image (if pillow installed)

  edge_cases:
    - Run from non-project directory
    - Run without gh CLI
    - Run without network
    - Run with missing dependencies
```

**Duration**: ~2-3 minutes (parallel execution)

---

### Phase 2: Install SoulHub

**Purpose**: Install SoulHub in test mode

**Actions**:
1. Create temporary test directory: `~/soulhub-e2e-test-{timestamp}/`
2. Copy repo to test directory (or use existing repo)
3. Create Python virtual environment
4. Install base dependencies: `pip install -e .`
5. Verify installation: `soulhub --version`
6. Check for SyntaxWarnings (should be none after bug fixes)

**Success Criteria**:
- ✅ Installation completes without errors
- ✅ `soulhub --version` returns "soulhub, version 1.0.0"
- ✅ No SyntaxWarnings in stderr
- ✅ All 8 core commands listed in `soulhub --help`

**Failure Handling**:
- Installation fails: Capture error, check dependencies, retry once
- Version check fails: ABORT (critical failure)
- SyntaxWarnings detected: WARN (should be fixed, but continue)

---

### Phase 3: Create Test Task List

**Purpose**: Generate comprehensive test plan based on research

**Task List Template**:
```yaml
tasks:
  - id: T1
    name: "Test soulhub --version"
    command: "soulhub --version"
    expected: "soulhub, version 1.0.0"
    critical: true

  - id: T2
    name: "Test soulhub --help"
    command: "soulhub --help"
    expected: "Lists all 8 commands"
    critical: true

  - id: T3
    name: "Test soulhub verify (from repo root)"
    command: "soulhub verify"
    expected: "8/15 tests pass"
    critical: true

  - id: T4
    name: "Test soulhub init"
    command: "soulhub init --name e2e-test-project"
    expected: "Creates .soulhub/ structure"
    critical: true

  - id: T5
    name: "Test soulhub status"
    command: "cd e2e-test-project && soulhub status"
    expected: "Shows project configuration"
    critical: true

  - id: T6
    name: "Test soulhub verify (from project)"
    command: "cd e2e-test-project && soulhub verify"
    expected: "11/15 tests pass (14/15 with gh)"
    critical: true

  - id: T7
    name: "Test soulhub catalog"
    command: "soulhub catalog"
    expected: "Shows 5 example souls"
    critical: false

  - id: T8
    name: "Test soulhub catalog search"
    command: "soulhub catalog -q medical"
    expected: "Filters to medical-assistant"
    critical: false

  - id: T9
    name: "Test soulhub archive"
    command: "cd e2e-test-project && soulhub archive"
    expected: "0 sessions found (expected)"
    critical: false

  - id: T10
    name: "Test verify_installation.py directly"
    command: "python verify_installation.py"
    expected: "8/15 tests pass from repo root"
    critical: true

  # Optional feature tests (run if dependencies available)
  - id: T11
    name: "Test real-time server (v1.1.0)"
    command: "timeout 5s soulhub serve"
    expected: "Server starts (if websockets installed)"
    critical: false
    requires: ["websockets"]

  - id: T12
    name: "Test corrections detection (v1.2.0)"
    command: "soulhub corrections"
    expected: "Scans for corrections (if available)"
    critical: false
    requires: ["torch"]

  - id: T13
    name: "Test multi-modal image storage (v1.3.0)"
    command: "echo 'test' > test.txt && soulhub remember-image test.txt --description 'test'"
    expected: "Stores image metadata (if pillow installed)"
    critical: false
    requires: ["pillow"]
```

**Task Generation Logic**:
1. Always include critical tests (T1-T6, T10)
2. Include optional tests (T7-T9)
3. Include feature tests only if dependencies detected
4. Mark tests as critical/non-critical based on importance
5. Set expected pass/fail criteria for each test

---

### Phase 4: Execute Test Suite

**Purpose**: Run all tests with detailed logging and validation

**Execution Strategy**:

#### 4.1 Critical Tests (Must Pass)
Run in order, ABORT on first failure:
```bash
# T1: Version check
soulhub --version 2>&1 | tee test-T1.log
# Expected: "soulhub, version 1.0.0"
# Validation: Exit code 0, version string present, no warnings

# T2: Help check
soulhub --help 2>&1 | tee test-T2.log
# Expected: All 8 commands listed
# Validation: Exit code 0, "init", "deploy", "archive", "sync", "catalog", "install", "verify", "status" all present

# T3: Verify from repo root
soulhub verify 2>&1 | tee test-T3.log
# Expected: "Tests Passed: 8/15"
# Validation: Exit code 1 (some tests fail), 8/15 ratio

# T4: Init new project
soulhub init --name e2e-test-project 2>&1 | tee test-T4.log
# Expected: Creates .soulhub/ directory with config.json and souls/
# Validation: Exit code 0, .soulhub/ exists, config.json valid JSON

# T5: Status check
cd e2e-test-project && soulhub status 2>&1 | tee ../test-T5.log
# Expected: Shows configuration without errors
# Validation: Exit code 0, displays project info

# T6: Verify from project
cd e2e-test-project && soulhub verify 2>&1 | tee ../test-T6.log
# Expected: "Tests Passed: 11/15" (or 14/15 with gh)
# Validation: Exit code 1, 11+/15 ratio

# T10: Direct verification script
python verify_installation.py 2>&1 | tee test-T10.log
# Expected: 8/15 from repo root
# Validation: Runs without errors, shows test report
```

**Validation Per Test**:
- Capture stdout, stderr, exit code
- Compare against expected values
- Take timestamp before/after (measure duration)
- Log pass/fail with reason
- Screenshot if applicable (N/A for CLI)

**Failure Handling**:
- Critical test fails: ABORT, generate failure report
- Non-critical test fails: LOG, continue
- Unexpected error: Capture traceback, continue if possible

#### 4.2 Optional Tests (Nice to Have)
Run after critical tests pass:
```bash
# T7-T9: Core optional commands
soulhub catalog 2>&1 | tee test-T7.log
soulhub catalog -q medical 2>&1 | tee test-T8.log
cd e2e-test-project && soulhub archive 2>&1 | tee ../test-T9.log

# Feature tests (only if dependencies available)
if websockets_installed:
  timeout 5s soulhub serve 2>&1 | tee test-T11.log

if torch_installed:
  soulhub corrections 2>&1 | tee test-T12.log

if pillow_installed:
  echo 'test' > test.txt
  soulhub remember-image test.txt --description 'test' 2>&1 | tee test-T13.log
```

#### 4.3 Edge Case Testing
Test error handling and edge cases:
```bash
# Test 1: Run from wrong directory
cd /tmp && soulhub status 2>&1 | tee edge-test-1.log
# Expected: Error about not being in a SoulHub project

# Test 2: Run without network (catalog)
# (Simulate by using local catalog-example.json)
soulhub catalog 2>&1 | tee edge-test-2.log
# Expected: Falls back to local catalog, shows 5 souls

# Test 3: Run verify without script
# (Temporarily rename verify_installation.py)
mv verify_installation.py verify_installation.py.bak
soulhub verify 2>&1 | tee edge-test-3.log
mv verify_installation.py.bak verify_installation.py
# Expected: Helpful error message with fallback instructions

# Test 4: Test with missing gh CLI (if not installed)
# Expected: Graceful degradation in init command
```

**Duration**: ~5-10 minutes for full suite

---

### Phase 5: Cleanup

**Purpose**: Stop any running processes and clean up test artifacts

**Actions**:
1. Stop any background servers (soulhub serve if running)
2. Deactivate virtual environment
3. Optionally delete test directory: `~/soulhub-e2e-test-{timestamp}/`
   - Ask user: "Delete test directory? (y/n)"
   - If yes: `rm -rf ~/soulhub-e2e-test-{timestamp}/`
   - If no: Keep for manual inspection
4. Clean up temporary files (test.txt, *.log if requested)
5. Reset to original directory

**Verification**:
- No processes left running (check with `ps aux | grep soulhub`)
- No stale lock files
- Clean exit

---

### Phase 6: Generate Report

**Purpose**: Provide comprehensive test results summary

**Report Format**:

#### 6.1 Text Summary (Console Output)
```
═══════════════════════════════════════════════════════════════
              SoulHub E2E Test Report
═══════════════════════════════════════════════════════════════

Test Run: 2026-02-26 08:30:15
Duration: 8m 23s
Environment: Windows 11 / Python 3.12.10 / Git 2.50.0
Repo: soulhub-cli @ commit c0cc816

═══════════════════════════════════════════════════════════════
SUMMARY
═══════════════════════════════════════════════════════════════

Total Tests: 13
Passed: 11 ✓
Failed: 2 ✗
Skipped: 0 ⊘

Critical Tests: 6/6 ✓ PASS
Optional Tests: 5/7 ✓ PARTIAL

Overall: ✓ PASS (85% success rate)

═══════════════════════════════════════════════════════════════
CRITICAL TESTS (Must Pass)
═══════════════════════════════════════════════════════════════

✓ T1  soulhub --version           0.2s  PASS
✓ T2  soulhub --help               0.3s  PASS
✓ T3  soulhub verify (repo)        3.1s  PASS (8/15)
✓ T4  soulhub init                 2.5s  PASS
✓ T5  soulhub status               0.4s  PASS
✓ T6  soulhub verify (project)     3.8s  PASS (11/15)

═══════════════════════════════════════════════════════════════
OPTIONAL TESTS
═══════════════════════════════════════════════════════════════

✓ T7  soulhub catalog              1.2s  PASS (5 souls)
✓ T8  catalog search               0.8s  PASS (filtered)
✓ T9  soulhub archive              0.5s  PASS (0 sessions)
✓ T10 verify_installation.py       3.2s  PASS (8/15)
✗ T11 real-time server             -     SKIP (websockets not installed)
✗ T12 corrections detection        -     SKIP (torch not installed)
✓ T13 multi-modal storage          0.6s  PASS

═══════════════════════════════════════════════════════════════
EDGE CASE TESTS
═══════════════════════════════════════════════════════════════

✓ Wrong directory error            0.3s  PASS (correct error)
✓ Catalog offline fallback         0.9s  PASS (local catalog)
✓ Verify path resolution           0.5s  PASS (found script)
✓ Init without gh CLI              2.1s  PASS (graceful warning)

═══════════════════════════════════════════════════════════════
ISSUES DETECTED
═══════════════════════════════════════════════════════════════

None - all tests passed! 🎉

═══════════════════════════════════════════════════════════════
RECOMMENDATIONS
═══════════════════════════════════════════════════════════════

✓ Core system (v1.0.0) is fully functional
⚠ Optional features not tested (missing dependencies):
  - Install websockets: pip install -r requirements-realtime.txt
  - Install torch: pip install -r requirements-training.txt

Next Steps:
1. Test with GitHub CLI authenticated (gh auth login)
2. Install optional dependencies for full feature testing
3. Test on a production deployment (soulhub deploy)
4. Test real-time coordination with multiple agents

═══════════════════════════════════════════════════════════════
```

#### 6.2 Detailed Markdown Report (Optional Export)
**File**: `soulhub-e2e-report-{timestamp}.md`

```markdown
# SoulHub E2E Test Report

**Generated**: 2026-02-26 08:30:15
**Duration**: 8m 23s
**Repo**: soulhub-cli @ commit c0cc816
**Environment**: Windows 11, Python 3.12.10, Git 2.50.0

---

## Executive Summary

- **Total Tests**: 13
- **Passed**: 11 ✓
- **Failed**: 2 ✗
- **Success Rate**: 85%
- **Critical Tests**: 6/6 ✓ ALL PASSED
- **Overall Status**: ✓ PASS

---

## Test Results Detail

### T1: Version Check ✓
**Command**: `soulhub --version`
**Duration**: 0.2s
**Status**: PASS

**Output**:
```
soulhub, version 1.0.0
```

**Validation**:
- ✓ Exit code 0
- ✓ Version string present
- ✓ No warnings detected

---

### T2: Help Command ✓
**Command**: `soulhub --help`
**Duration**: 0.3s
**Status**: PASS

**Output**:
```
Usage: soulhub [OPTIONS] COMMAND [ARGS]...

Commands:
  init     Initialize a new SoulHub project
  deploy   Deploy to GitHub + Cloudflare
  archive  Archive conversations
  sync     Sync souls across agents
  catalog  Browse soul catalog
  install  Install soul from catalog
  verify   Run verification tests
  status   Show project status
```

**Validation**:
- ✓ All 8 commands listed
- ✓ Help text formatted correctly

---

[... detailed output for each test ...]

---

## Performance Metrics

| Test | Duration | Status |
|------|----------|--------|
| T1 - Version | 0.2s | ✓ |
| T2 - Help | 0.3s | ✓ |
| T3 - Verify (repo) | 3.1s | ✓ |
| T4 - Init | 2.5s | ✓ |
| T5 - Status | 0.4s | ✓ |
| T6 - Verify (project) | 3.8s | ✓ |
| T7 - Catalog | 1.2s | ✓ |
| T8 - Catalog search | 0.8s | ✓ |
| T9 - Archive | 0.5s | ✓ |
| T10 - Verification script | 3.2s | ✓ |
| T13 - Multi-modal | 0.6s | ✓ |

**Total Execution Time**: 16.6s (excluding skipped tests)

---

## Dependency Analysis

### Installed
- ✓ click
- ✓ requests
- ✓ gitpython
- ✓ tigs
- ✓ pillow

### Not Installed (Optional)
- ✗ websockets (v1.1.0 real-time features)
- ✗ redis (v1.1.0 pub/sub)
- ✗ torch (v1.2.0 training features)
- ✗ transformers (v1.2.0)

---

## Issues & Recommendations

### Critical Issues
None detected ✓

### Warnings
- Real-time features not testable (websockets not installed)
- Training features not testable (torch not installed)

### Recommendations
1. Install optional dependencies for comprehensive testing:
   ```bash
   pip install -r requirements-realtime.txt
   pip install -r requirements-training.txt
   ```

2. Test with GitHub CLI authenticated:
   ```bash
   gh auth login
   soulhub init --name production-test
   soulhub deploy
   ```

3. Test multi-agent coordination:
   ```bash
   soulhub serve  # Terminal 1
   soulhub connect --agent-id test-1  # Terminal 2
   ```

---

## Next Steps

1. ✅ Core system validated and working
2. ⏳ Install optional dependencies
3. ⏳ Test with gh CLI authentication
4. ⏳ Test production deployment workflow
5. ⏳ Test real-time multi-agent coordination
6. ⏳ Test auto-training pipeline
7. ⏳ Deploy to cloud LLM for validation

---

**Report Generated By**: SoulHub E2E Test Skill v1.0.0
**Test Engineer**: Claude Sonnet 4.5
```

---

## Skill Usage

### Basic Usage
```bash
# From Claude Code
/skill soulhub-e2e-test

# Or with custom options
/skill soulhub-e2e-test --install-optional-deps --export-report
```

### Configuration Options
```yaml
options:
  install_optional_deps: false  # Auto-install websockets, torch, etc.
  export_markdown_report: true  # Generate detailed .md report
  cleanup_after_test: true      # Delete test directory after completion
  verbose_logging: false        # Show detailed command output
  skip_edge_cases: false        # Skip edge case testing
  timeout_per_test: 30          # Seconds before test times out
```

### Expected Runtime
- **Minimal** (critical tests only): ~2-3 minutes
- **Standard** (critical + optional): ~5-8 minutes
- **Comprehensive** (all tests + edge cases): ~10-15 minutes

---

## Success Criteria

### Minimum (v1.0.0 Core)
- ✅ All 6 critical tests pass
- ✅ soulhub verify reports 8/15 from repo root
- ✅ soulhub verify reports 11/15 from project (14/15 with gh)
- ✅ No SyntaxWarnings
- ✅ No critical bugs detected

### Optimal (All Features)
- ✅ All critical tests pass
- ✅ 10/13 total tests pass
- ✅ Real-time server starts successfully
- ✅ Training pipeline functional
- ✅ Multi-modal storage working
- ✅ All edge cases handled gracefully

---

## Troubleshooting

### Test Failures

**If T1 (version) fails**:
- Check SoulHub is installed: `pip list | grep soulhub`
- Reinstall: `pip install -e .`
- Check for Python errors in installation

**If T3/T6 (verify) fails**:
- Check verify_installation.py exists
- Run directly: `python verify_installation.py`
- Check for missing dependencies

**If T4 (init) fails**:
- Check Git is installed
- Check write permissions
- Try with different project name

### Common Issues

**"Verification script not found"**:
- Make sure you're in the soulhub-cli directory
- Check verify_installation.py exists
- This was fixed in commit 66098ed

**"Network error" in catalog**:
- Expected if offline
- Should fallback to local catalog-example.json
- Check catalog-example.json exists

**"GitHub CLI not found"**:
- Expected if gh not installed
- Tests will show 11/15 instead of 14/15
- Install with: `brew install gh` or visit https://cli.github.com

---

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: SoulHub E2E Tests

on: [push, pull_request]

jobs:
  e2e-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install SoulHub
        run: pip install -e .

      - name: Run E2E Tests
        run: |
          # Would call this skill via Claude Code CLI
          # Or run tests directly
          python verify_installation.py
          soulhub verify

      - name: Upload test reports
        uses: actions/upload-artifact@v3
        with:
          name: e2e-test-reports
          path: soulhub-e2e-report-*.md
```

---

## Maintenance

### Updating This Skill

When SoulHub adds new features:
1. Add new test tasks to Phase 3
2. Update expected pass rates in Phase 4
3. Add new dependencies to Phase 1 Sub-Agent 2
4. Update success criteria
5. Re-run full test suite to validate

### Version History
- **v1.0.0** (2026-02-26): Initial release
  - Tests v1.0.0 core features
  - Tests v1.1.0-v1.3.0 optional features
  - Comprehensive edge case testing
  - Markdown report generation

---

## License
MIT License - Same as SoulHub CLI
