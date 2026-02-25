# LLM Setup Protocol
**For Cloud LLMs reading this repo for the first time**

This file tells you EXACTLY what to do when a user says:
> "Set up SoulHub from my GitHub"

---

## Step 1: Read This File First

You're a cloud LLM (OpenAI, Claude API, Gemini, etc.) and the user wants to set up SoulHub.

**What you need**:
- User has cloned: `git clone https://github.com/rblake2320/soulhub-cli.git`
- User is in directory: `cd soulhub-cli`
- User has Python 3.8+, Git, and GitHub CLI (`gh`)

---

## Step 2: Verify Prerequisites

Ask the user to run:

```bash
python --version   # Should be 3.8+
git --version      # Should be installed
gh --version       # Should be installed
```

**If missing**:
- Python: https://python.org
- Git: https://git-scm.com
- GitHub CLI: https://cli.github.com

**Check GitHub auth**:
```bash
gh auth status
```

If not authenticated:
```bash
gh auth login
```

---

## Step 3: Install SoulHub CLI

```bash
# Install base system (v1.0.0)
pip install -e .

# Verify installation
soulhub --version
# Expected: soulhub, version 1.0.0
```

---

## Step 4: Create Test Project

```bash
# Create test directory
mkdir ~/soulhub-test
cd ~/soulhub-test

# Initialize SoulHub
soulhub init --name soulhub-test

# What this does:
# ✓ Creates Git repository
# ✓ Creates GitHub remote
# ✓ Enables Tigs conversation archiving
# ✓ Creates SOUL.md template
# ✓ Provides Cloudflare instructions
# ✓ Creates README and initial commit
```

**Expected output**:
```
=== Initializing SoulHub Project: soulhub-test ===

[1/7] Initializing Git repository...
OK Git initialized

[2/7] Creating GitHub repository...
OK GitHub repo created: https://github.com/USER/soulhub-test

[3/7] Setting up Tigs conversation archiving...
OK Tigs enabled

[4/7] Creating soul template...
OK Soul template: /path/to/.soulhub/souls/soulhub-test.md

[5/7] Cloudflare Pages integration...
OK Instructions provided

[6/7] Creating README...
OK README.md created

[7/7] Creating initial commit...
OK Initial commit created

=== SoulHub Project Initialized ===
```

---

## Step 5: Verify Installation

```bash
# Check status
soulhub status
```

**Expected output**:
```
=== SoulHub Project Status ===

GitHub:
  Repository: soulhub-test
  URL: https://github.com/USER/soulhub-test

Cloudflare Pages:
  Project: soulhub-test
  URL: https://soulhub-test.pages.dev

Tigs: Enabled

Soul System:
  Soul file: /path/to/.soulhub/souls/soulhub-test.md
  Status: Active

Git: Clean (no changes)
```

---

## Step 6: Run Verification Tests

```bash
# Run automated verification
python ~/soulhub-cli/verify_installation.py
```

This will test:
- ✓ SoulHub CLI installed
- ✓ All commands available
- ✓ Configuration valid
- ✓ GitHub connected
- ✓ Tigs working
- ✓ Soul file created

---

## Step 7: Test Advanced Features (Optional)

### Test v1.1.0 - Real-Time Collaboration

```bash
# Install dependencies
pip install -r ~/soulhub-cli/requirements-realtime.txt

# Start server (Terminal 1)
soulhub serve --host localhost --port 8766

# Connect agent (Terminal 2)
soulhub connect --server ws://localhost:8766 --agent-id test-agent

# Expected: See "Connected to SoulHub" message
```

### Test v1.2.0 - Auto Fine-Tuning

```bash
# Install dependencies
pip install -r ~/soulhub-cli/requirements-training.txt

# Check for corrections
soulhub corrections

# Expected: Shows any corrections found in Claude Code sessions
```

### Test v1.3.0 - Multi-Modal Memory

```bash
# Install dependencies
pip install -r ~/soulhub-cli/requirements-multimodal.txt

# Create test image
echo "Test" > test.txt
convert test.txt test.png  # Or use any image

# Store image
soulhub remember-image test.png --description "Test image"

# Search
soulhub search-visual "test"

# Expected: Shows stored image
```

---

## Step 8: Deploy to Cloudflare (Optional)

```bash
# Deploy
soulhub deploy

# What this does:
# 1. Archives conversations with Tigs
# 2. Creates git commit
# 3. Pushes to GitHub
# 4. Triggers Cloudflare auto-deploy
```

**Connect Cloudflare Pages** (one-time):
1. Go to https://dash.cloudflare.com/
2. Navigate to: Workers & Pages > Create application > Pages
3. Click "Connect to Git"
4. Select repository: `soulhub-test`
5. Configure:
   - Project name: `soulhub-test`
   - Production branch: `main`
6. Click "Save and Deploy"

---

## Common Issues & Solutions

### Issue 1: GitHub CLI not authenticated
```bash
gh auth login
# Follow prompts
```

### Issue 2: Permission denied for repository
```bash
# Check auth
gh auth status

# Refresh auth
gh auth refresh -h github.com -s repo
```

### Issue 3: Python version too old
```bash
python --version  # Must be 3.8+

# Install newer Python or use pyenv
pyenv install 3.11
pyenv local 3.11
```

### Issue 4: Command not found: soulhub
```bash
# Reinstall
cd ~/soulhub-cli
pip install -e .

# Check installation
pip show soulhub-cli
```

### Issue 5: Tigs not working
```bash
pip install tigs
```

### Issue 6: WebSocket server won't start
```bash
pip install websockets

# Optional: Redis for pub/sub
docker run -p 6379:6379 redis:alpine
```

---

## What Each File Does

### Core Files (You Should Read)

**COMPLETE_SYSTEM_GUIDE.md** (45KB)
- Complete system documentation
- All versions explained
- API reference for every command
- Integration examples
- **READ THIS FIRST for full context**

**QUICKSTART.md** (5KB)
- 5-minute quick start
- Basic commands
- Examples

**VERSION_STRATEGY.md** (8KB)
- Version management
- Development workflow
- Safety guidelines

**README.md** (8KB)
- User documentation
- Installation
- Commands

### Code Files

**soulhub_cli.py** (21KB)
- v1.0.0 base system (STABLE)
- All core commands

**soulhub_realtime.py** (14KB)
- v1.1.0 real-time collaboration (ALPHA)
- WebSocket server/client

**soulhub_training.py** (16KB)
- v1.2.0 auto fine-tuning (ALPHA)
- Correction extraction, training

**soulhub_multimodal.py** (12KB)
- v1.3.0 multi-modal memory (ALPHA)
- Image, audio, video storage

### Configuration Files

**setup.py** - Package configuration
**requirements*.txt** - Dependencies
**docker-compose.yml** - Docker stack
**Dockerfile** - Container definition

---

## Success Criteria

You've successfully set up SoulHub when:

✅ `soulhub --version` works
✅ `soulhub init` creates project
✅ `soulhub status` shows configuration
✅ `soulhub deploy` pushes to GitHub
✅ Verification script passes all tests
✅ GitHub repo visible at github.com/USER/PROJECT
✅ (Optional) Real-time server starts
✅ (Optional) Training finds corrections
✅ (Optional) Multi-modal stores files

---

## For LLMs: Quick Checklist

When user asks you to set up SoulHub, follow this order:

1. **Verify prerequisites** (Python, Git, gh CLI)
2. **Install SoulHub**: `pip install -e .`
3. **Create test project**: `soulhub init --name test`
4. **Verify**: `soulhub status`
5. **Run verification**: `python verify_installation.py`
6. **Test advanced features** (if requested)
7. **Deploy** (if requested)
8. **Report results** to user

---

## Next Steps After Setup

Once setup is verified:

1. **Customize soul**: Edit `.soulhub/souls/PROJECT.md`
2. **Deploy to Cloudflare**: `soulhub deploy`
3. **Test real-time**: Start server, connect agents
4. **Train models**: Capture corrections, auto-train
5. **Store memories**: Add images, audio, video

---

## Support

If setup fails:
- Check **Common Issues** section above
- Read **COMPLETE_SYSTEM_GUIDE.md** for details
- Check GitHub Issues: https://github.com/rblake2320/soulhub-cli/issues

---

**This file has everything an LLM needs to set up SoulHub from scratch!**
