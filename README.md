<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/logo-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/logo-light.svg">
  <img alt="DeskPilot" src="docs/logo-light.svg" width="400">
</picture>

# DeskPilot

**Pilot Any Desktop. Automate Any Application. No API Required.**

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-0066CC" alt="Platform">
  <img src="https://img.shields.io/badge/AI-100%25%20Local-00AA55" alt="AI">
  <img src="https://img.shields.io/badge/GPU-Not%20Required-FF6600" alt="GPU">
  <img src="https://img.shields.io/badge/License-MIT-AAAAAA" alt="License">
</p>

---

## Executive Summary

**DeskPilot transforms any computer into an AI-powered automation platform.**

That Windows XP machine running your critical manufacturing software? The Mac mini controlling your digital signage? The lab computer running decade-old instrument software? DeskPilot gives them all an AI brain that can see, understand, and operate any application—just like a human would.

### 100% Self-Contained. Air-Gapped Capable. No Cloud Required.

DeskPilot runs **entirely on local hardware**—including the AI models. Using CPU-optimized models (Qwen 2.5, 3B parameters), DeskPilot operates on standard hardware without expensive GPUs or cloud connectivity.

| Deployment Scenario | DeskPilot Capability |
|---------------------|---------------------|
| **Air-gapped networks** | Zero internet required after setup |
| **Healthcare (HIPAA)** | PHI never leaves premises |
| **Defense systems** | Classified environment compatible |
| **Remote facilities** | Works offline indefinitely |

### The Problem

Organizations have billions invested in software that:
- Has no API or integration capabilities
- Runs only on specific hardware or legacy OS
- Requires manual, repetitive human interaction
- Cannot be modernized without significant cost

### The Solution

DeskPilot provides a universal integration layer for **any application with a screen**:

```
"Open the inventory system, find items below threshold,
 and export them to a spreadsheet"
```

DeskPilot executes this across applications that were never designed to work together.

---

## Architecture

```mermaid
block-beta
    columns 5

    block:USER:5
        columns 5
        CLI["Command Line"] CHAT["Slack/Teams"] SOCIAL["Telegram"] API["REST API"] WEB["Web UI"]
    end

    space:5

    block:ORCHESTRATION:5
        columns 3
        GATEWAY["OpenClaw Gateway"]
        SKILLS["Skills Library"]
        AI["Local AI (Ollama)"]
    end

    space:5

    block:CONTROL:5
        columns 3
        CUA["Cua SDK"]
        VISION["Screen Capture"]
        INPUT["Mouse & Keyboard"]
    end

    space:5

    block:TARGETS:5
        columns 3
        WIN["Windows"]
        MAC["macOS"]
        LINUX["Linux"]
    end

    space:5

    block:APPS:5
        columns 4
        LAB["Lab Equipment"]
        LEGACY["Legacy Apps"]
        DESKTOP["Desktop Software"]
        CUSTOM["Custom Tools"]
    end

    USER --> ORCHESTRATION
    ORCHESTRATION --> CONTROL
    CONTROL --> TARGETS
    TARGETS --> APPS
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Interface** | OpenClaw Gateway | Multi-channel routing (CLI, chat, API) |
| **AI Engine** | Ollama + Qwen 2.5 | **CPU-only** local inference |
| **Skills** | Markdown + YAML | Shareable automation recipes |
| **Control** | Cua SDK | Cross-platform screen/input automation |
| **Sandbox** | Lume / Docker / QEMU | Isolated VM environments |

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 4 cores @ 2.5 GHz | 8+ cores @ 3.0 GHz |
| **RAM** | 8 GB | 16 GB |
| **Storage** | 10 GB | 50 GB SSD |
| **GPU** | **Not required** | Optional (faster) |
| **Network** | **Not required** | Optional |

**Runs on:** Intel i5+, AMD Ryzen 5+, Apple M1+, ARM64

---

## Real-World Applications

### Laboratory & Scientific Equipment

| System | Challenge | DeskPilot Solution |
|--------|-----------|-------------------|
| **Mass Spectrometers** | 2005 vendor software, no API | Natural language data extraction |
| **DNA Sequencers** | Windows XP only | Automated run scheduling |
| **Oscilloscopes** | Manual screenshot capture | Continuous monitoring |
| **Chromatography** | Proprietary formats | AI-powered reporting |

### Air-Gapped & Secure Environments

| Environment | Requirement | Capability |
|-------------|-------------|-----------|
| **Defense** | Zero connectivity | 100% offline operation |
| **Healthcare** | HIPAA compliance | Local AI, no cloud |
| **Finance** | Regulatory audit | Full action logging |
| **Critical Infrastructure** | OT/IT separation | VM isolation |

### Legacy Business Systems

| Category | Examples | Potential |
|----------|----------|-----------|
| **Industrial** | SCADA, HMI panels | ChatOps monitoring |
| **Finance** | Trading terminals | Automated reporting |
| **Retail** | DOS-based POS | Modern integration |
| **Manufacturing** | CNC controls | Remote operation |
| **Media** | Winamp, VLC | Voice control |

---

## The Calculator Demo

DeskPilot uses **Skills**—modular recipes that teach the AI to operate applications.

```bash
# Install
git clone https://github.com/usathyan/deskpilot && cd deskpilot
make install

# Run the demo
deskpilot demo
```

### What Happens

1. DeskPilot **launches Calculator** via Start menu
2. You type: `"Calculate 15 times 8"`
3. AI **analyzes the screen**, identifies buttons
4. DeskPilot **clicks**: 1 → 5 → × → 8 → =
5. **Returns**: `120`

```
┌─────────────────────────────────────┐
│  DeskPilot Calculator Demo          │
└─────────────────────────────────────┘

> Calculate 15 * 8

  Step 1: Launching Calculator...
  Step 2: Clicking [1]
  Step 3: Clicking [5]
  Step 4: Clicking [×]
  Step 5: Clicking [8]
  Step 6: Clicking [=]

┌──────────────┐
│  Result: 120 │
└──────────────┘
```

---

## Build & Share Skills

Every application you automate becomes a reusable skill.

### Example: Winamp Skill

```yaml
# skills/winamp/SKILL.md
name: winamp
description: Control Winamp media player

capabilities:
  - Play/pause/stop
  - Navigate playlists
  - Adjust volume
  - Search songs

examples:
  - "Play my 90s playlist at 70% volume"
  - "Skip to the next song"
  - "What's currently playing?"
```

### Share With the Community

```bash
deskpilot skill package ./my-skill
deskpilot skill publish my-skill
```

**Every skill you create helps someone else automate their legacy systems.**

---

## Deployment Options

> **Important:** DeskPilot runs on your **HOST machine** and controls the **TARGET** (VM or native desktop) remotely via screen capture and input injection. You do NOT install DeskPilot inside the VM.

```
┌─────────────────────────────────────────────────────────────────┐
│  HOST MACHINE (where you install DeskPilot)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ DeskPilot    │  │ Ollama AI    │  │ Cua SDK      │          │
│  │ CLI          │  │ (qwen2.5)    │  │              │          │
│  └──────┬───────┘  └──────────────┘  └──────┬───────┘          │
│         │                                    │                  │
│         └────────────────┬───────────────────┘                  │
│                          │ Controls                             │
│                          ▼                                      │
│         ┌────────────────────────────────────┐                  │
│         │  TARGET: VM or Native Desktop      │                  │
│         │  (Calculator, apps, legacy software)│                  │
│         └────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Step 1: Install DeskPilot on Your HOST Machine

```bash
# Clone the repository
git clone https://github.com/usathyan/deskpilot
cd deskpilot

# Create virtual environment and install
make venv
source .venv/bin/activate
make install

# Install Ollama and download AI model (~2GB)
brew install ollama   # or: curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen2.5:3b
```

---

### Step 2: Set Up Your TARGET (Choose One)

#### Option A: macOS VM via Lume (Apple Silicon & Intel)

```bash
# Install Lume
brew install lume

# Create and run a macOS VM
lume create --os macOS --ipsw latest deskpilot-vm
lume run deskpilot-vm

# Configure DeskPilot to use the VM
cat > config/local.yaml << 'EOF'
deployment:
  mode: vm
vm:
  os_type: macos
  provider_type: lume
EOF
```

#### Option B: Windows VM via Docker (Linux Host)

```bash
# Start Windows 11 VM
docker-compose up -d

# Access via web browser
open http://localhost:8006

# Configure DeskPilot
cat > config/local.yaml << 'EOF'
deployment:
  mode: vm
vm:
  os_type: windows
  provider_type: docker
EOF
```

#### Option C: Native Mode (Control Your Own Desktop)

```bash
# No VM needed - DeskPilot controls your current machine
cat > config/local.yaml << 'EOF'
deployment:
  mode: native
EOF
```

---

### Step 3: Run DeskPilot

```bash
# Make sure your VM is running (if using VM mode)
# Then run the demo from your HOST machine:
deskpilot demo
```

---

### Remote Machine

Connect to a VM running on another host:

```yaml
# config/local.yaml
vm:
  provider_type: cloud
  host: 192.168.1.100
```

---

## ROI Impact

| Task | Manual | With DeskPilot |
|------|--------|----------------|
| Data entry (1000 records) | 8 hours | 15 minutes |
| Daily report generation | 2 hours | 2 minutes |
| System monitoring | 4 hrs/day | Continuous |
| Operator training | 2 weeks | 1 day |

**Typical savings: 70-90% on repetitive GUI tasks.**

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/usathyan/deskpilot
cd deskpilot
make venv && source .venv/bin/activate
make install

# Setup AI model (one-time, ~2GB download)
ollama pull qwen2.5:3b

# Configure
deskpilot setup

# Run demo
deskpilot demo
```

### Chat Platform Integration

```bash
# Install OpenClaw
npm install -g openclaw@latest

# Connect Slack
openclaw channel add slack --token xoxb-your-token

# Control from Slack
# @deskpilot screenshot the dashboard
```

---

## Security

| Concern | DeskPilot Approach |
|---------|-------------------|
| **Data Privacy** | 100% local AI |
| **Air-Gapped** | Fully offline capable |
| **Audit Trail** | Complete action logging |
| **Isolation** | VM sandboxing |
| **Access Control** | OpenClaw IAM integration |

---

## Roadmap

- [x] Core automation engine
- [x] Multi-platform (Windows, macOS, Linux)
- [x] Calculator demo skill
- [ ] Skill marketplace
- [ ] Visual skill builder
- [ ] Enterprise SSO
- [ ] Scheduled triggers
- [ ] Multi-machine orchestration

---

## License

MIT License — Free for commercial and personal use.

---

<p align="center">
  <b>DeskPilot: Because every desktop deserves an AI co-pilot.</b>
  <br><br>
  <a href="#quick-start">Get Started</a> ·
  <a href="#build--share-skills">Build Skills</a> ·
  <a href="https://github.com/usathyan/deskpilot/discussions">Community</a>
</p>
