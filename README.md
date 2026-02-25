# SoulHub CLI

**All-in-One AI Memory & Deployment System**

Combines GitHub + Cloudflare Pages + Tigs + Soul System into a single command-line tool.

## What It Does

SoulHub CLI integrates best-in-class tools:
- **GitHub** - Version control + catalog registry
- **Cloudflare Pages** - Global CDN + auto-deployment
- **Tigs** - Conversation archiving in Git
- **Soul System** - Decision trees, verification, pattern learning, cross-LLM compatibility

## Installation

```bash
# Install from source
git clone https://github.com/rblake2320/soulhub-cli.git
cd soulhub-cli
pip install -e .

# Or install from PyPI (when published)
pip install soulhub-cli
```

## Prerequisites

- Python 3.8+
- Git installed
- GitHub CLI (`gh`) - [Install here](https://cli.github.com/)
- Cloudflare account (free tier works)

## Quick Start

```bash
# Create a new soul project
mkdir my-ai-project
cd my-ai-project
soulhub init --name my-ai-project

# Deploy to GitHub + Cloudflare
soulhub deploy

# Archive your AI conversations
soulhub archive

# Check status
soulhub status
```

## Commands

### `soulhub init`
Initialize a new SoulHub project with:
- Git repository
- GitHub remote (via `gh` CLI)
- Soul template (SOUL.md)
- Tigs conversation archiving
- Cloudflare Pages integration instructions
- README and initial commit

```bash
soulhub init --name my-project [--private]
```

### `soulhub deploy`
Deploy your project:
1. Archives Claude Code conversations with Tigs
2. Creates git commit
3. Pushes to GitHub
4. Cloudflare Pages auto-deploys from GitHub

```bash
soulhub deploy
```

### `soulhub archive`
Archive Claude Code conversations to Git using Tigs:

```bash
soulhub archive
```

### `soulhub sync`
Sync souls across AI agents:

```bash
soulhub sync spark-1 192.168.12.132
soulhub sync windows-claude vps-agent
```

### `soulhub catalog`
Browse or search the soul catalog:

```bash
# List all souls
soulhub catalog

# Search for specific souls
soulhub catalog --query "medical"
```

### `soulhub install`
Install a soul from the catalog:

```bash
soulhub install expert-coder
soulhub install medical-assistant
```

### `soulhub verify`
Run verification tests on your soul system:

```bash
soulhub verify
```

### `soulhub status`
Show project status (GitHub, Cloudflare, Tigs, Soul System):

```bash
soulhub status
```

## How It Works

### 1. GitHub Integration
- Uses GitHub CLI (`gh`) to create repositories
- Manages remotes and pushes automatically
- Acts as catalog registry for souls

### 2. Cloudflare Pages Integration
- Connects GitHub repo to Cloudflare Pages
- Auto-deploys on every git push
- Global CDN with unlimited bandwidth (free tier)
- HTTPS by default

### 3. Tigs Conversation Archiving
- Stores Claude Code sessions in Git
- Uses Git refs (`.git/refs/tigs/chats/`)
- Conversations versioned without modifying commits
- Searchable and permanent

### 4. Soul System
- Persistent AI memory (SOUL.md)
- Decision archaeology (why→what→outcome chains)
- Pattern learning engine
- Cross-agent synchronization
- Verification framework
- Cross-LLM compatibility (OpenAI, Gemini, Llama)

## Project Structure

After running `soulhub init`, your project will have:

```
my-ai-project/
├── .git/                      # Git repository
│   └── refs/tigs/            # Tigs conversation storage
├── .soulhub/                 # SoulHub configuration
│   ├── config.json           # Project config
│   └── souls/                # Soul templates
│       └── my-project.md     # Your soul file
├── README.md                 # Auto-generated README
└── .gitignore                # Standard ignores
```

## Configuration

Configuration is stored in `.soulhub/config.json`:

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
  }
}
```

## Examples

### Create and Deploy a New Project

```bash
# Create project
mkdir my-ai-assistant
cd my-ai-assistant

# Initialize SoulHub
soulhub init --name my-ai-assistant

# Edit your soul
vim .soulhub/souls/my-ai-assistant.md

# Deploy
soulhub deploy

# Your project is now live at:
# - GitHub: https://github.com/you/my-ai-assistant
# - Cloudflare: https://my-ai-assistant.pages.dev
```

### Archive and Search Conversations

```bash
# Archive all Claude Code sessions
soulhub archive

# Commit archived conversations
git add . && git commit -m "Archive conversations"

# Push to GitHub (auto-deploys to Cloudflare)
soulhub deploy

# Later: search archived conversations
git log --all --grep="soul system"
```

### Sync Souls Across AI Army

```bash
# Sync Windows Claude soul to Spark-1
soulhub sync windows-claude 192.168.12.132

# Sync Spark-1 soul to VPS
soulhub sync spark-1 76.13.118.222
```

### Browse and Install Souls

```bash
# Browse catalog
soulhub catalog

# Search for medical souls
soulhub catalog --query medical

# Install a soul template
soulhub install medical-assistant

# Merge into your soul
cat .soulhub/souls/medical-assistant.md >> .soulhub/souls/my-project.md
```

## Architecture

SoulHub CLI leverages existing infrastructure:

```
┌─────────────────────────────────────────────┐
│         SOULHUB CLI (This Tool)             │
│  - Decision archaeology                     │
│  - Pain point prevention database           │
│  - Cross-LLM soul converter                 │
│  - Verification framework                   │
│  - AI Army coordination                     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   EXISTING INFRASTRUCTURE (Free & Fast)     │
│  - GitHub (catalog + version control)       │
│  - Cloudflare Pages (CDN + auto-deploy)     │
│  - Tigs (conversation archiving)            │
└─────────────────────────────────────────────┘
```

## What Makes This Novel

While individual components exist (GitHub, Cloudflare, Tigs), SoulHub CLI adds:

1. **Decision Archaeology** - Track why→what→outcome chains (not in other tools)
2. **Verification Framework** - Proof your soul system works (5 automated tests)
3. **Cross-LLM Compatibility** - Use souls with OpenAI, Gemini, Llama
4. **AI Army Coordination** - Sync souls across multiple agents
5. **Pain Point Database** - Global mistake prevention
6. **All-in-One CLI** - Single command for entire workflow

## Roadmap

- [ ] Publish to PyPI
- [ ] Create public soul catalog registry
- [ ] Add pattern voting/curation
- [ ] Build decision marketplace
- [ ] Add pain point submission
- [ ] Create web UI for catalog
- [ ] Add soul forking/merging
- [ ] Implement federated learning
- [ ] Cross-LLM testing suite
- [ ] Mobile app integration

## Contributing

Contributions welcome! This is the early stage of building a global AI memory network.

## License

MIT License - See LICENSE file

## Links

- [Soul System](https://github.com/rblake2320/soul-system) - Core soul engine
- [Tigs](https://github.com/welldefined-ai/tigs) - Conversation archiving
- [Cloudflare Pages](https://pages.cloudflare.com/) - Deployment platform
- [GitHub CLI](https://cli.github.com/) - GitHub integration

## Credits

Built on the shoulders of:
- OpenClaw (SOUL.md concept)
- Tigs (Git-based chat archiving)
- Cloudflare (CDN infrastructure)
- GitHub (Version control + registry)
- Claude Code (AI development environment)

---

**Built by**: rblake2320
**Version**: 1.0.0
**Status**: Beta
