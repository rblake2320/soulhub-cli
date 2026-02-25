# SoulHub Quick Start

Get up and running in 5 minutes.

## Installation

```bash
# Clone repository
git clone https://github.com/rblake2320/soulhub-cli.git
cd soulhub-cli

# Install
pip install -e .

# Verify
soulhub --version
```

## Create Your First Project

```bash
# Create project directory
mkdir my-ai-project
cd my-ai-project

# Initialize SoulHub
soulhub init --name my-ai-project

# You'll see:
# ✅ Git initialized
# ✅ GitHub repo created
# ✅ Tigs enabled
# ✅ Soul template created
# ✅ Cloudflare instructions
# ✅ README created
# ✅ Initial commit
```

## Deploy to Cloudflare Pages

```bash
# Push to GitHub (auto-triggers Cloudflare)
soulhub deploy

# Your site will be live at:
# https://my-ai-project.pages.dev
```

## Connect Cloudflare Pages (One-Time Setup)

1. Go to https://dash.cloudflare.com/
2. Navigate to: **Workers & Pages** > **Create application** > **Pages**
3. Click **Connect to Git**
4. Select your GitHub repository: `my-ai-project`
5. Configure:
   - **Project name**: `my-ai-project`
   - **Production branch**: `main`
   - Click **Save and Deploy**

Done! Every `soulhub deploy` will now auto-deploy.

## Customize Your Soul

```bash
# Edit your soul file
vim .soulhub/souls/my-ai-project.md
```

Add your preferences:
```markdown
## Communication Style
- Prefer direct, concise answers
- Use bullet points
- Skip pleasantries

## Pain Points Solved
- Never use long-winded explanations when asked for quick answer
```

Save and deploy:
```bash
soulhub deploy
```

Now every chat session will remember your preferences!

## Advanced Features

### Real-Time Collaboration (v1.1.0)

```bash
# Install dependencies
pip install -r requirements-realtime.txt

# Start server
soulhub serve

# In another terminal, connect agent
soulhub connect --agent-id windows-claude

# In another terminal, connect another agent
soulhub connect --agent-id spark-1

# Now they communicate in real-time!
```

### Auto Fine-Tuning (v1.2.0)

```bash
# Install dependencies
pip install -r requirements-training.txt
curl -fsSL https://ollama.com/install.sh | sh

# Pull base model
ollama pull llama3.1:70b

# Train from corrections
soulhub corrections  # See what you've corrected
soulhub train        # Train model automatically

# Use trained model
ollama run soulhub-llama3
```

### Multi-Modal Memory (v1.3.0)

```bash
# Install dependencies
pip install -r requirements-multimodal.txt

# Store image
soulhub remember-image screenshot.png --description "UI design"

# Store voice note
soulhub remember-voice voice.mp3 --description "Tone preference"

# Search visual memory
soulhub search-visual "UI design"
```

## Docker Deployment

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f soulhub-server

# Stop services
docker-compose down
```

Services running:
- SoulHub server: `ws://localhost:8766`
- Redis: `redis://localhost:6379`
- Ollama: `http://localhost:11434`
- PostgreSQL: `postgresql://localhost:5432/soulhub`

## Browse Soul Catalog

```bash
# List all souls
soulhub catalog

# Search for specific souls
soulhub catalog --query "medical"

# Install a soul
soulhub install expert-coder
```

## Check Project Status

```bash
soulhub status
```

Output:
```
GitHub:
  Repository: my-ai-project
  URL: https://github.com/you/my-ai-project

Cloudflare Pages:
  Project: my-ai-project
  URL: https://my-ai-project.pages.dev

Tigs: Enabled
Soul System: Active
Git: Clean
```

## Next Steps

- **Read full documentation**: [README.md](README.md)
- **See all commands**: `soulhub --help`
- **Complete guide**: [COMPLETE_SYSTEM_GUIDE.md](COMPLETE_SYSTEM_GUIDE.md)
- **Version strategy**: [VERSION_STRATEGY.md](VERSION_STRATEGY.md)
- **Join community**: [GitHub Discussions](https://github.com/rblake2320/soulhub-cli/discussions)

## Troubleshooting

**Issue**: GitHub CLI not authenticated
```bash
gh auth login
```

**Issue**: Cloudflare not deploying
- Check GitHub repo is connected in Cloudflare dashboard
- Verify production branch is set to `main`

**Issue**: Tigs not working
```bash
pip install tigs
```

**Issue**: Real-time server won't start
```bash
pip install websockets redis
docker run -p 6379:6379 redis:alpine
```

## Support

- **GitHub Issues**: https://github.com/rblake2320/soulhub-cli/issues
- **Discussions**: https://github.com/rblake2320/soulhub-cli/discussions
- **Email**: [Create an issue instead]

---

**That's it! You're ready to build with SoulHub** 🚀
