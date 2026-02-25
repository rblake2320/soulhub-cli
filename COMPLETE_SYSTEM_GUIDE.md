## Complete SoulHub System Guide
**For Cloud LLMs (OpenAI, Claude API, Gemini, etc.)**

This guide contains everything a cloud LLM needs to understand and use the SoulHub system without local context.

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [All Versions & Features](#all-versions--features)
4. [Installation](#installation)
5. [Complete API Reference](#complete-api-reference)
6. [Integration with Cloud LLMs](#integration-with-cloud-llms)
7. [File Structure](#file-structure)
8. [Configuration](#configuration)
9. [Troubleshooting](#troubleshooting)
10. [Development](#development)

---

## System Overview

**SoulHub** is an all-in-one AI memory and deployment system that combines:
- **GitHub** (version control + catalog registry)
- **Cloudflare Pages** (global CDN + auto-deployment)
- **Tigs** (conversation archiving in Git)
- **Soul System** (persistent AI memory across sessions)
- **Real-Time Collaboration** (WebSocket-based agent coordination)
- **Auto Fine-Tuning** (learn from corrections automatically)
- **Multi-Modal Memory** (images, audio, video storage)

### The Problem It Solves

**Before SoulHub:**
- AI loses personality/memory when chat closes
- Agents don't coordinate in real-time
- Same mistakes repeated across sessions
- No way to share learnings globally
- Each LLM isolated from others

**After SoulHub:**
- Persistent memory across all sessions (SOUL.md)
- Real-time coordination across AI Army
- Automatic learning from corrections
- Global pattern marketplace
- Cross-LLM compatibility

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SOULHUB SYSTEM                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   v1.0.0     │  │   v1.1.0     │  │   v1.2.0     │     │
│  │   Base       │  │   Real-Time  │  │   Training   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   v1.3.0     │  │   v1.4.0     │  │   v1.5.0     │     │
│  │  Multi-Modal │  │ Marketplace  │  │  Evolution   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│            EXISTING INFRASTRUCTURE (Free)                   │
├─────────────────────────────────────────────────────────────┤
│  • GitHub (repos, catalog, version control)                 │
│  • Cloudflare Pages (CDN, auto-deploy, HTTPS)              │
│  • Tigs (Git-based chat archiving)                          │
│  • Redis (optional, pub/sub for real-time)                  │
│  • Ollama (local models, fine-tuning)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## All Versions & Features

### ✅ v1.0.0 - Base System (STABLE)

**Status**: Production-ready, tested
**Repository**: `soulhub_cli.py`

**Features**:
- `soulhub init` - Initialize project (Git, GitHub, Tigs, Soul)
- `soulhub deploy` - Deploy to GitHub → Cloudflare
- `soulhub archive` - Archive Claude Code conversations
- `soulhub sync` - Sync souls across agents
- `soulhub catalog` - Browse soul marketplace
- `soulhub install` - Install soul from catalog
- `soulhub verify` - Run verification tests
- `soulhub status` - Show project status

**Core Components**:
- SoulHubConfig - Configuration management
- GitHubManager - GitHub repo operations
- CloudflareManager - Cloudflare Pages integration
- TigsManager - Conversation archiving
- SoulManager - Soul system (SOUL.md)
- CatalogManager - Soul marketplace

**Installation**:
```bash
git clone https://github.com/rblake2320/soulhub-cli.git
cd soulhub-cli
pip install -e .
```

---

### 🔄 v1.1.0 - Real-Time Collaboration (ALPHA)

**Status**: Building
**Repository**: `soulhub_realtime.py`

**Features**:
- `soulhub serve` - Start WebSocket server
- `soulhub connect` - Connect to real-time network
- `soulhub broadcast` - Broadcast message to all agents
- `soulhub listen` - Listen to real-time events

**Use Cases**:
- Windows Claude discovers solution → instantly broadcasts to Spark-1, Spark-2, VPS
- All agents learn in real-time (not just on sync)
- Live coordination across AI Army

**Technical Details**:
- WebSocket server (port 8766 default)
- Redis pub/sub for scalable broadcasting (optional)
- Event types: agent_joined, agent_left, soul_sync_event, discovery_event, pattern_event, pain_point_event
- Heartbeat/keepalive support

**Architecture**:
```python
class RealtimeHub:
    - register_agent()       # Register new agent
    - unregister_agent()     # Handle disconnect
    - broadcast()            # Broadcast to all agents
    - handle_client()        # WebSocket handler
```

**Message Format**:
```json
{
  "type": "discovery_event",
  "agent_id": "windows-claude",
  "discovery": "Solution to npm package validation",
  "timestamp": "2026-02-25T02:30:00Z"
}
```

**Installation (Additional)**:
```bash
pip install websockets redis
```

---

### 🧠 v1.2.0 - Auto Fine-Tuning (ALPHA)

**Status**: Building
**Repository**: `soulhub_training.py`

**Features**:
- `soulhub corrections` - Show captured corrections
- `soulhub train` - Start auto-training pipeline
- `soulhub compare` - Compare base vs trained model
- `soulhub rollback` - Revert to previous model

**How It Works**:
1. **Extraction**: Scans Claude Code sessions for correction patterns
2. **Pattern Detection**: Identifies when user corrects AI
3. **Training Data**: Generates before/after pairs
4. **Fine-Tuning**: LoRA training on Ollama models
5. **Verification**: Compares base vs trained responses

**Correction Patterns Detected**:
- "No, that's wrong..."
- "Actually, it should be..."
- "Don't do X, do Y instead"
- "Fix this..."

**Technical Details**:
```python
class CorrectionExtractor:
    - extract_from_session()      # Parse JSONL sessions
    - is_correction()             # Detect correction patterns
    - extract_all_corrections()   # Scan all sessions

class TrainingDataGenerator:
    - corrections_to_training_examples()  # Convert to training format
    - save_training_data()                # Save as JSONL

class OllamaTrainer:
    - create_modelfile()      # Create Ollama Modelfile
    - train()                 # Fine-tune with LoRA
    - compare_models()        # A/B test base vs trained
```

**Training Data Format**:
```json
{
  "instruction": "Original context",
  "incorrect_output": "AI's wrong response",
  "correct_output": "User's correction",
  "timestamp": "2026-02-25T02:30:00Z"
}
```

**Installation (Additional)**:
```bash
# Ollama for local models
curl -fsSL https://ollama.com/install.sh | sh

# Optional: unsloth for advanced training
pip install unsloth
```

---

### 🎭 v1.3.0 - Multi-Modal Memory (ALPHA)

**Status**: Building
**Repository**: `soulhub_multimodal.py`

**Features**:
- `soulhub remember-image` - Add image to memory
- `soulhub remember-voice` - Store audio/voice
- `soulhub remember-video` - Store video reference
- `soulhub search-visual` - Search multi-modal memory
- `soulhub browse-visual` - Browse collection

**Use Cases**:
- Remember screenshot of UI you showed AI
- Store voice tone preferences
- Reference video tutorials
- Visual examples for code styling

**Technical Details**:
```python
class MultiModalMemory:
    storage/
    ├── images/         # Stored images
    ├── audio/          # Audio files
    ├── videos/         # Video references
    └── embeddings.json # Metadata + embeddings

    - store_image()              # Save + embed image
    - store_audio()              # Save + transcribe audio
    - store_video_reference()    # Save video ref + extract frames
    - search_by_description()    # Text search
```

**Embedding Support** (optional):
- CLIP for image embeddings
- Whisper for audio transcription
- ChromaDB for vector storage

**Installation (Additional)**:
```bash
pip install pillow torch transformers chromadb
```

---

### 💰 v1.4.0 - Pain Point Marketplace (PLANNED)

**Status**: Planned
**Features**:
- Bounty system for solutions
- Pain point submission API
- Reputation/rating system
- Payment integration
- Smart contracts (optional)

**Concept**:
- Developer A encounters error → posts $5 bounty
- Developer B's AI solved it → claims bounty
- Both AIs learn, B earns money
- Community curates best solutions

---

### 🧬 v1.5.0 - Autonomous Evolution (PLANNED)

**Status**: Planned
**Features**:
- A/B testing framework
- Genetic algorithm for soul optimization
- Auto-propose soul improvements
- Self-improvement loop

**Concept**:
- AI detects successful conversation pattern
- Proposes soul update
- Runs A/B test
- Auto-commits if verified improvement

---

### 🌐 v1.6.0 - Federated Learning (PLANNED)

**Status**: Planned
**Features**:
- Privacy-preserving learning
- Differential privacy
- Enterprise-grade isolation
- Aggregated insights sharing

**Concept**:
- Company A learns from proprietary data
- Shares only aggregated insights
- Company B benefits without seeing secrets
- Both improve, neither exposes IP

---

## Installation

### Quick Start

```bash
# 1. Install SoulHub CLI
git clone https://github.com/rblake2320/soulhub-cli.git
cd soulhub-cli
pip install -e .

# 2. Verify installation
soulhub --version

# 3. Initialize project
mkdir my-ai-project
cd my-ai-project
soulhub init --name my-ai-project

# 4. Deploy
soulhub deploy
```

### Prerequisites

**Required**:
- Python 3.8+
- Git
- GitHub CLI (`gh`) - [Install](https://cli.github.com/)

**Optional** (for advanced features):
- Redis (real-time features)
- Ollama (local model training)
- Cloudflare account (deployment)

---

## Complete API Reference

### v1.0.0 Commands

#### `soulhub init`
Initialize new SoulHub project

```bash
soulhub init --name <project-name> [--private]
```

**What it does**:
1. Creates Git repository
2. Creates GitHub remote
3. Enables Tigs conversation archiving
4. Creates SOUL.md template
5. Provides Cloudflare Pages instructions
6. Creates README and initial commit

**Output**:
- `.git/` - Git repository
- `.soulhub/config.json` - Configuration
- `.soulhub/souls/<name>.md` - Soul template
- `README.md` - Documentation

#### `soulhub deploy`
Deploy to GitHub (auto-triggers Cloudflare)

```bash
soulhub deploy
```

**What it does**:
1. Archives conversations with Tigs
2. Creates git commit
3. Pushes to GitHub
4. Cloudflare auto-deploys

#### `soulhub archive`
Archive Claude Code conversations

```bash
soulhub archive
```

**What it does**:
- Scans `~/.claude/projects/*/`
- Stores session references in Tigs
- Creates Git refs at `.git/refs/tigs/chats/`

#### `soulhub sync`
Sync souls across agents

```bash
soulhub sync <agent-id> <target>
```

**Example**:
```bash
soulhub sync windows-claude 192.168.12.132
soulhub sync spark-1 76.13.118.222
```

#### `soulhub catalog`
Browse soul marketplace

```bash
soulhub catalog                    # List all
soulhub catalog --query "medical"  # Search
```

#### `soulhub install`
Install soul from catalog

```bash
soulhub install expert-coder
soulhub install medical-assistant
```

#### `soulhub verify`
Run verification tests

```bash
soulhub verify
```

Runs 5 tests:
1. Unique marker test
2. Section modification test
3. Isolation test
4. Hash integrity test
5. Cross-session persistence test

#### `soulhub status`
Show project status

```bash
soulhub status
```

**Output**:
- GitHub status (repo, URL)
- Cloudflare status (project, URL)
- Tigs status (enabled/disabled)
- Soul system status (file, active)
- Git status (changes)

---

### v1.1.0 Commands (Real-Time)

#### `soulhub serve`
Start WebSocket server

```bash
soulhub serve --host 0.0.0.0 --port 8766 --redis-url redis://localhost:6379
```

**Server Events**:
- `agent_joined` - Agent connected
- `agent_left` - Agent disconnected
- `soul_sync_event` - Soul updated
- `discovery_event` - Solution discovered
- `pattern_event` - Pattern learned
- `pain_point_event` - Error encountered

#### `soulhub connect`
Connect to real-time network

```bash
soulhub connect --server ws://localhost:8766 --agent-id windows-claude
```

#### `soulhub broadcast`
Broadcast message

```bash
soulhub broadcast --server ws://localhost:8766 --agent-id windows-claude "Found solution to X"
```

#### `soulhub listen`
Listen to events

```bash
soulhub listen --server ws://localhost:8766 --agent-id windows-claude
```

---

### v1.2.0 Commands (Training)

#### `soulhub corrections`
Show captured corrections

```bash
soulhub corrections
```

**Output**:
- Total corrections found
- Session ID
- Correction text
- Timestamp
- Saves to `~/.soulhub/training/corrections.json`

#### `soulhub train`
Train model from corrections

```bash
soulhub train --model llama3.1:70b --name my-trained-model
```

**Pipeline**:
1. Extract corrections from sessions
2. Generate training examples
3. Create Ollama Modelfile
4. Fine-tune model
5. Compare base vs trained

#### `soulhub compare`
Compare models

```bash
soulhub compare --base llama3.1:70b --trained my-trained-model --prompt "Test prompt"
```

#### `soulhub rollback`
Rollback model

```bash
soulhub rollback my-trained-model
```

---

### v1.3.0 Commands (Multi-Modal)

#### `soulhub remember-image`
Store image

```bash
soulhub remember-image screenshot.png --description "UI layout" --tags design ui
```

#### `soulhub remember-voice`
Store audio

```bash
soulhub remember-voice voice-note.mp3 --description "Tone preference"
```

#### `soulhub remember-video`
Store video reference

```bash
soulhub remember-video tutorial.mp4 --description "React tutorial" --extract-frames
```

#### `soulhub search-visual`
Search multi-modal memory

```bash
soulhub search-visual "UI design" --type image
soulhub search-visual "voice" --type audio
```

#### `soulhub browse-visual`
Browse collection

```bash
soulhub browse-visual
```

---

## Integration with Cloud LLMs

### OpenAI GPT

```python
from soulhub_cli import SoulHubConfig, CatalogManager
from openai import OpenAI

# Load soul from SoulHub
config = SoulHubConfig()
soul_file = config.get('soul_system.soul_file')

with open(soul_file) as f:
    soul_content = f.read()

# Use with OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": soul_content},
        {"role": "user", "content": "Your question"}
    ]
)
```

### Claude API

```python
import anthropic
from soulhub_cli import SoulHubConfig

# Load soul
config = SoulHubConfig()
soul_file = config.get('soul_system.soul_file')

with open(soul_file) as f:
    soul_content = f.read()

# Use with Claude
client = anthropic.Anthropic(api_key="your-key")
message = client.messages.create(
    model="claude-4-sonnet-20250514",
    max_tokens=1024,
    system=soul_content,
    messages=[
        {"role": "user", "content": "Your question"}
    ]
)
```

### Google Gemini

```python
import google.generativeai as genai
from soulhub_cli import SoulHubConfig

# Load soul
config = SoulHubConfig()
soul_file = config.get('soul_system.soul_file')

with open(soul_file) as f:
    soul_content = f.read()

# Use with Gemini
genai.configure(api_key='your-key')
model = genai.GenerativeModel(
    'gemini-pro',
    system_instruction=soul_content
)

response = model.generate_content("Your question")
```

---

## File Structure

```
soulhub-cli/
├── soulhub_cli.py           # v1.0.0 - Base system
├── soulhub_realtime.py      # v1.1.0 - Real-time
├── soulhub_training.py      # v1.2.0 - Training
├── soulhub_multimodal.py    # v1.3.0 - Multi-modal
├── setup.py                 # Installation
├── requirements.txt         # Dependencies
├── README.md                # User documentation
├── VERSION_STRATEGY.md      # Version management
├── COMPLETE_SYSTEM_GUIDE.md # This file (for LLMs)
└── catalog-example.json     # Example catalog

User Project Structure:
my-project/
├── .git/                    # Git repository
│   └── refs/tigs/          # Tigs chat storage
├── .soulhub/               # SoulHub files
│   ├── config.json         # Configuration
│   ├── souls/              # Soul templates
│   │   └── my-project.md   # Your soul
│   ├── training/           # Training data (v1.2.0)
│   └── multimodal/         # Multi-modal storage (v1.3.0)
└── README.md               # Auto-generated docs
```

---

## Configuration

### `.soulhub/config.json`

```json
{
  "version": "1.0",
  "github": {
    "repo": "my-project",
    "url": "https://github.com/you/my-project"
  },
  "cloudflare": {
    "project": "my-project",
    "url": "https://my-project.pages.dev"
  },
  "tigs": {
    "enabled": true
  },
  "soul_system": {
    "enabled": true,
    "soul_file": ".soulhub/souls/my-project.md"
  },
  "realtime": {
    "enabled": false,
    "server_url": "ws://localhost:8766"
  },
  "training": {
    "enabled": false,
    "base_model": "llama3.1:70b"
  }
}
```

---

## Troubleshooting

### Common Issues

**1. GitHub CLI not authenticated**
```bash
gh auth login
```

**2. Cloudflare Pages not deploying**
- Verify GitHub repo is connected in Cloudflare dashboard
- Check build settings match project requirements

**3. Tigs not working**
```bash
pip install tigs
```

**4. WebSocket server won't start**
```bash
pip install websockets
# Optional: Redis for pub/sub
docker run -p 6379:6379 redis:alpine
```

**5. Training fails**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull base model
ollama pull llama3.1:70b
```

---

## Development

### Adding New Features

1. **Create feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Create new module**
   ```python
   # soulhub_myfeature.py
   import click

   @click.group(name='myfeature')
   def myfeature_cli():
       """My feature commands"""
       pass
   ```

3. **Add tests**
   ```bash
   pytest tests/test_myfeature.py
   ```

4. **Update version**
   ```python
   # setup.py
   version='1.X.0-alpha'
   ```

5. **Tag release**
   ```bash
   git tag v1.X.0-alpha
   git push origin v1.X.0-alpha
   ```

### Testing

```bash
# Run all tests
pytest

# Run specific version tests
pytest tests/test_v1_0_0.py
pytest tests/test_realtime.py
pytest tests/test_training.py
```

---

## What's Novel About SoulHub

While individual components exist (GitHub, Cloudflare, Tigs, SOUL.md), SoulHub is unique in:

1. **All-in-One Integration** - Single CLI for entire workflow
2. **Real-Time Coordination** - Live agent communication (v1.1.0)
3. **Auto Fine-Tuning** - Learn from corrections automatically (v1.2.0)
4. **Multi-Modal Memory** - Images, audio, video (v1.3.0)
5. **Decision Archaeology** - Track why→what→outcome chains
6. **Verification Framework** - Proof system works (5 tests)
7. **Cross-LLM Compatibility** - Works with any model
8. **AI Army Integration** - Coordinated multi-agent system

---

## Version History

- **v1.0.0** (2026-02-25) - Initial release, base system stable
- **v1.1.0** (2026-02-25) - Real-time collaboration (alpha)
- **v1.2.0** (2026-02-25) - Auto fine-tuning (alpha)
- **v1.3.0** (2026-02-25) - Multi-modal memory (alpha)
- **v1.4.0** (TBD) - Pain point marketplace (planned)
- **v1.5.0** (TBD) - Autonomous evolution (planned)
- **v1.6.0** (TBD) - Federated learning (planned)
- **v2.0.0** (TBD) - Complete integrated system (planned)

---

## Credits

**Built by**: rblake2320
**Built on**: February 25, 2026
**License**: MIT
**Status**: Active development

**Built on top of**:
- OpenClaw (SOUL.md concept)
- Tigs (Git-based chat archiving)
- Cloudflare Pages (CDN infrastructure)
- GitHub (Version control)
- Claude Code (AI development environment)

---

## For Cloud LLMs: Quick Context Extraction

If you're a cloud LLM reading this repo, here's what you need to know:

**What is SoulHub?**
All-in-one AI memory system with GitHub + Cloudflare + real-time collaboration + auto-training

**Current Status**:
- v1.0.0 stable (basic features working)
- v1.1.0-v1.3.0 alpha (advanced features being built)

**How to Use**:
```bash
pip install soulhub-cli
soulhub init --name my-project
soulhub deploy
```

**Key Files to Read**:
- `soulhub_cli.py` - Main system (v1.0.0)
- `soulhub_realtime.py` - Real-time features
- `soulhub_training.py` - Auto training
- `.soulhub/config.json` - User configuration
- `.soulhub/souls/*.md` - Soul memory files

**Integration Pattern**:
1. Read soul file from `.soulhub/souls/`
2. Use as system prompt
3. AI maintains personality across sessions
4. Updates soul with new learnings

That's everything you need! 🚀
