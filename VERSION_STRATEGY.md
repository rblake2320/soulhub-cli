# SoulHub Version Strategy

**Goal**: Build new features without breaking working v1.0.0

## Version Plan

### ✅ v1.0.0 (STABLE - Current)
**Status**: Tested and working
**Features**:
- GitHub integration (repo creation, push)
- Cloudflare Pages setup instructions
- Tigs conversation archiving
- Soul system (SOUL.md templates)
- Cross-agent sync
- Verification framework
- Catalog browsing/install
- Basic CLI commands

**DO NOT MODIFY** - This is our stable baseline

---

### 🔄 v1.1.0 - Real-Time Collaboration (Building)
**Branch**: `feature/realtime-collaboration`
**New Features**:
- WebSocket server for real-time agent communication
- Redis pub/sub message broker
- Live soul synchronization across AI Army
- Event broadcasting (discoveries, solutions, patterns)
- Real-time status dashboard

**Tech Stack**:
- WebSockets (socket.io or websockets library)
- Redis for pub/sub
- Real-time event streaming

**Commands to add**:
- `soulhub serve` - Start WebSocket server
- `soulhub connect <agent>` - Connect to real-time network
- `soulhub broadcast <message>` - Broadcast to all agents
- `soulhub listen` - Listen to real-time events

---

### 🧠 v1.2.0 - Auto Fine-Tuning (Building)
**Branch**: `feature/auto-finetuning`
**New Features**:
- Capture user corrections automatically
- Generate training examples from conversations
- LoRA fine-tuning pipeline for local models
- Auto-train on Ollama models
- Verification that model improved

**Tech Stack**:
- unsloth (fast LoRA training)
- Ollama integration
- Training data extraction from Claude sessions
- Model comparison before/after

**Commands to add**:
- `soulhub train` - Start auto-training pipeline
- `soulhub corrections` - Show captured corrections
- `soulhub compare` - Compare base vs trained model
- `soulhub rollback` - Revert to previous model

---

### 🎭 v1.3.0 - Multi-Modal Memory (Building)
**Branch**: `feature/multimodal-memory`
**New Features**:
- Store images in soul memory
- Voice tone preferences
- Video references
- Multi-modal vector embeddings
- Visual soul browser

**Tech Stack**:
- CLIP for image embeddings
- Whisper for audio transcription
- ChromaDB for vector storage
- Multi-modal retrieval

**Commands to add**:
- `soulhub remember-image <path>` - Add image to memory
- `soulhub remember-voice <audio>` - Store voice preference
- `soulhub browse-visual` - Visual memory explorer

---

### 💰 v1.4.0 - Pain Point Marketplace (Future)
**Branch**: `feature/marketplace`
**New Features**:
- Bounty system for solutions
- Pain point submission
- Reputation/rating system
- Payment integration
- Smart contracts (optional)

**Tech Stack**:
- Payment API (Stripe/crypto)
- Reputation system
- Bounty matching algorithm

---

### 🧬 v1.5.0 - Autonomous Evolution (Future)
**Branch**: `feature/autonomous-evolution`
**New Features**:
- A/B testing framework
- Genetic algorithm for soul optimization
- Auto-propose soul improvements
- Automated verification of changes
- Self-improvement loop

**Tech Stack**:
- A/B testing framework
- Genetic algorithms
- Automated metrics collection

---

### 🌐 v1.6.0 - Federated Learning (Future)
**Branch**: `feature/federated-learning`
**New Features**:
- Privacy-preserving learning
- Differential privacy
- Secure multi-party computation
- Enterprise-grade isolation
- Aggregated insights sharing

**Tech Stack**:
- TensorFlow Federated
- Differential privacy libraries
- Homomorphic encryption

---

### 🚀 v2.0.0 - Complete System (Future)
**Branch**: `release/v2.0.0`
**Status**: Combines all features when tested
**Release Criteria**:
- All v1.x features tested individually
- Integration tests pass
- Performance benchmarks meet targets
- Documentation complete
- Security audit passed

---

## Development Workflow

### For Each New Feature

1. **Create Feature Branch**
   ```bash
   cd ~/soulhub-cli
   git checkout -b feature/realtime-collaboration
   ```

2. **Develop in Isolation**
   - New code in separate modules
   - Don't modify v1.0.0 core files
   - Add new commands, don't change existing ones

3. **Test Independently**
   ```bash
   # Test new feature without affecting v1.0.0
   python -m pytest tests/test_realtime.py
   ```

4. **Version Bump**
   ```bash
   # In setup.py
   version='1.1.0-alpha'
   ```

5. **Tag Release**
   ```bash
   git tag v1.1.0-alpha
   git push origin v1.1.0-alpha
   ```

6. **Keep v1.0.0 Accessible**
   ```bash
   # Users can install stable version
   pip install soulhub-cli==1.0.0

   # Or test new features
   pip install soulhub-cli==1.1.0-alpha
   ```

---

## File Organization

```
soulhub-cli/
├── soulhub_cli.py          # v1.0.0 core (DON'T MODIFY)
├── soulhub_realtime.py     # v1.1.0 real-time features
├── soulhub_training.py     # v1.2.0 auto fine-tuning
├── soulhub_multimodal.py   # v1.3.0 multi-modal memory
├── soulhub_marketplace.py  # v1.4.0 marketplace
├── soulhub_evolution.py    # v1.5.0 autonomous evolution
├── soulhub_federated.py    # v1.6.0 federated learning
├── setup.py                # Version management
├── requirements.txt        # Base requirements
├── requirements-dev.txt    # Development requirements
└── tests/
    ├── test_v1_0_0.py     # v1.0.0 tests (must always pass)
    ├── test_realtime.py   # v1.1.0 tests
    ├── test_training.py   # v1.2.0 tests
    └── ...
```

---

## Safety Checklist

Before merging any new feature:

- [ ] v1.0.0 tests still pass
- [ ] New feature has its own tests
- [ ] No breaking changes to existing commands
- [ ] Documentation updated
- [ ] Version number bumped correctly
- [ ] Backward compatibility maintained
- [ ] Performance impact measured
- [ ] Security reviewed

---

## Rollback Plan

If something breaks:

```bash
# Revert to stable v1.0.0
pip uninstall soulhub-cli
pip install soulhub-cli==1.0.0

# Or use git
git checkout v1.0.0
pip install -e .
```

---

## Current Status (2026-02-25)

- ✅ v1.0.0 - Stable and tested
- 🔄 v1.1.0 - Building now (real-time collaboration)
- ⏳ v1.2.0 - Queued (auto fine-tuning)
- ⏳ v1.3.0 - Queued (multi-modal memory)
- 📋 v1.4.0+ - Planned

**Next action**: Build v1.1.0 real-time collaboration module
