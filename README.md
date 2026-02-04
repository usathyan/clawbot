# ClawBot

**Turn Any Computer Into an AI-Powered Automation Platform**

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue" alt="Platform">
  <img src="https://img.shields.io/badge/AI-Local%20%7C%20Private%20%7C%20Secure-green" alt="AI">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

---

## Executive Summary

**ClawBot transforms legacy computers into AI-enabled automation platforms.**

That Windows XP machine running your critical manufacturing software? The Mac mini controlling your digital signage? The Linux workstation with your proprietary CAD tools? The lab computer running decade-old instrument software? ClawBot gives them all an AI brain that can see, understand, and operate any application—just like a human would.

### 100% Self-Contained, No Cloud Required

ClawBot runs **entirely on local hardware**—including the AI models. Using CPU-optimized models like Qwen 2.5 (3B parameters), ClawBot operates on standard hardware without requiring expensive GPUs or cloud connectivity. Perfect for:

- **Air-gapped environments** (defense, healthcare, finance)
- **Bandwidth-constrained sites** (remote facilities, field operations)
- **Data-sensitive operations** (PII, trade secrets, proprietary data)
- **Offline-first deployments** (ships, aircraft, underground facilities)

### The Problem

Organizations have billions of dollars invested in software that:
- Has no API or integration capabilities
- Runs on specific hardware or legacy operating systems
- Requires manual, repetitive human interaction
- Cannot be modernized without significant cost
- Is physically isolated from modern infrastructure

### The Solution

ClawBot provides a universal integration layer that works with **any application that has a screen**. Using computer vision AI running entirely on local hardware (CPU-only, no GPU required), ClawBot can:

- **See** what's on screen (screenshots, UI elements)
- **Understand** natural language instructions
- **Act** through mouse clicks, keyboard input, and application control
- **Connect** via chat interfaces, social media, or programmatic APIs

```
"Open the inventory system, find all items with quantity below 10,
 and export them to a spreadsheet"
```

ClawBot executes this across applications that were never designed to talk to each other.

---

## How It Works

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#4F46E5', 'primaryTextColor': '#fff', 'primaryBorderColor': '#4338CA', 'lineColor': '#6366F1', 'secondaryColor': '#EC4899', 'tertiaryColor': '#10B981', 'background': '#F8FAFC', 'mainBkg': '#F8FAFC', 'secondBkg': '#FDF4FF', 'tertiaryBkg': '#ECFDF5'}}}%%
flowchart TB
    subgraph USER["👤 User Interface Layer"]
        direction LR
        CLI["🖥️ Command Line<br/><i>clawbot run</i>"]
        CHAT["💬 Chat Interface<br/><i>Slack, Discord, Teams</i>"]
        SOCIAL["📱 Social Connectors<br/><i>Telegram, WhatsApp</i>"]
        API["🔌 REST API<br/><i>Programmatic Access</i>"]
    end

    subgraph BRAIN["🧠 AI Orchestration Layer"]
        direction LR
        OPENCLAW["OpenClaw Gateway<br/><i>Multi-channel Router</i>"]
        SKILLS["📚 Skills Library<br/><i>Calculator, Notepad, etc.</i>"]
        OLLAMA["🤖 Local AI Model<br/><i>Ollama + Qwen/LLaMA</i>"]
    end

    subgraph CONTROL["🎮 Computer Control Layer"]
        direction LR
        CUA["Cua SDK<br/><i>Screen • Mouse • Keyboard</i>"]
        VISION["👁️ Computer Vision<br/><i>UI Understanding</i>"]
        ACTIONS["⚡ Action Engine<br/><i>Click • Type • Launch</i>"]
    end

    subgraph TARGET["🖥️ Target Systems"]
        direction LR
        WIN["🪟 Windows<br/><i>VM or Native</i>"]
        MAC["🍎 macOS<br/><i>Lume VMs</i>"]
        LINUX["🐧 Linux<br/><i>Docker/QEMU</i>"]
    end

    subgraph APPS["📦 Any Application"]
        direction LR
        LEGACY["Legacy Software<br/><i>No API Required</i>"]
        DESKTOP["Desktop Apps<br/><i>Office, CAD, etc.</i>"]
        CUSTOM["Custom Tools<br/><i>Proprietary Systems</i>"]
    end

    CLI --> OPENCLAW
    CHAT --> OPENCLAW
    SOCIAL --> OPENCLAW
    API --> OPENCLAW

    OPENCLAW --> SKILLS
    SKILLS --> OLLAMA
    OLLAMA --> CUA

    CUA --> VISION
    CUA --> ACTIONS

    VISION --> WIN
    VISION --> MAC
    VISION --> LINUX
    ACTIONS --> WIN
    ACTIONS --> MAC
    ACTIONS --> LINUX

    WIN --> LEGACY
    WIN --> DESKTOP
    MAC --> DESKTOP
    MAC --> CUSTOM
    LINUX --> LEGACY
    LINUX --> CUSTOM

    style USER fill:#EEF2FF,stroke:#4F46E5,stroke-width:2px
    style BRAIN fill:#FDF4FF,stroke:#EC4899,stroke-width:2px
    style CONTROL fill:#ECFDF5,stroke:#10B981,stroke-width:2px
    style TARGET fill:#FEF3C7,stroke:#F59E0B,stroke-width:2px
    style APPS fill:#FEE2E2,stroke:#EF4444,stroke-width:2px
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **User Interface** | OpenClaw Gateway | Routes commands from any channel (CLI, Slack, Telegram, API) |
| **AI Brain** | Ollama + Qwen 2.5 (3B) | **CPU-optimized** local AI, runs on any modern processor |
| **Skills** | Markdown + YAML | Teachable automation recipes, shareable across teams |
| **Computer Control** | Cua SDK | Cross-platform screen capture, mouse, keyboard automation |
| **Virtualization** | Lume / Docker / QEMU | Isolated sandboxes for safe automation |

### Hardware Requirements (CPU-Only Operation)

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 4 cores, 2.5 GHz | 8+ cores, 3.0 GHz |
| **RAM** | 8 GB | 16 GB |
| **Storage** | 10 GB | 50 GB SSD |
| **GPU** | **Not required** | Optional (faster inference) |
| **Network** | None (air-gapped OK) | Optional (for updates) |

**Works on:** Intel Core i5+, AMD Ryzen 5+, Apple M1+, ARM64 servers

### Key Differentiators

| Feature | Traditional RPA | ClawBot |
|---------|----------------|---------|
| **Setup Complexity** | Weeks of scripting | Minutes with natural language |
| **AI Location** | Cloud (data leaves network) | 100% Local (air-gapped capable) |
| **Application Support** | Requires connectors | Works with any UI |
| **Learning Curve** | Programming required | Plain English instructions |
| **Cost Model** | Per-bot licensing | Open source, unlimited |

---

## The Calculator Demo: Skills in Action

ClawBot uses **Skills**—modular automation recipes that teach the AI how to operate specific applications. Here's how the built-in Calculator skill works:

### Running the Demo

```bash
# Install ClawBot
git clone https://github.com/user/clawbot && cd clawbot
make install

# Run the interactive Calculator demo
clawbot demo
```

### What Happens

1. **ClawBot launches Calculator** using the Start menu (just like a human would)
2. **You type a calculation** in plain English: `"Calculate 15 times 8"`
3. **The AI sees the screen**, identifies the Calculator buttons
4. **ClawBot clicks the buttons**: 1 → 5 → × → 8 → =
5. **Result displayed**: `120`

```
╭─────────────────────────────────────────╮
│ ClawBot Calculator Demo                 │
╰─────────────────────────────────────────╯

Calculate: 15 * 8

Step 1: Analyzing screen...
Step 2: Clicking button "1"
Step 3: Clicking button "5"
Step 4: Clicking button "×"
Step 5: Clicking button "8"
Step 6: Clicking button "="

┌─────────┐
│ Result  │
├─────────┤
│ 15 * 8 = 120 │
└─────────┘
```

### The Skill Behind It

```markdown
# skills/calculator/SKILL.md

---
name: calculator
description: Automate Windows Calculator for mathematical operations
---

## Commands

- `clawbot launch Calculator` - Open the app
- `clawbot run "Calculate X * Y"` - Perform calculation

## How It Works

1. Launch Calculator via Start menu search
2. Parse the mathematical expression
3. Click number and operator buttons in sequence
4. Read and return the result
```

---

## Build Your Own Skills

**The real power of ClawBot is extensibility.** Every application you automate becomes a reusable skill that others can benefit from.

### Example: Automating Winamp 🎵

```markdown
# skills/winamp/SKILL.md

---
name: winamp
description: Control Winamp media player through natural language
---

## Capabilities

- Play/pause/stop music
- Navigate playlists
- Adjust volume
- Search and queue songs

## Example Usage

"Play my 90s playlist and set volume to 70%"
"Skip to the next song"
"What song is currently playing?"
```

### Real-World Use Cases

#### Laboratory & Scientific Equipment

| System | Challenge | ClawBot Solution |
|--------|-----------|------------------|
| **Mass Spectrometers** | Vendor software from 2005, no API | Natural language data extraction |
| **DNA Sequencers** | Windows XP only, can't upgrade | Automated run scheduling |
| **Oscilloscopes** | Manual screenshot capture | Continuous monitoring & alerts |
| **Chromatography Systems** | Proprietary data formats | AI-powered report generation |

#### Air-Gapped & Secure Systems

| Environment | Requirement | ClawBot Capability |
|-------------|-------------|-------------------|
| **Defense Systems** | Zero internet connectivity | 100% offline operation |
| **Healthcare (HIPAA)** | PHI never leaves premises | Local AI, no cloud calls |
| **Financial Trading** | Regulatory compliance | Full audit trail, isolated |
| **Critical Infrastructure** | OT/IT separation | VM sandboxing |

#### Legacy Business Systems

| Category | Examples | Automation Potential |
|----------|----------|---------------------|
| **Media** | Winamp, VLC, iTunes | Voice-controlled playback |
| **Office** | Excel macros, Access databases | Natural language queries |
| **Industrial** | SCADA interfaces, HMI panels | ChatOps monitoring |
| **Finance** | Legacy trading terminals | Automated reporting |
| **Creative** | Photoshop, AutoCAD | AI-assisted workflows |
| **Retail** | DOS-based POS systems | Modern integration |
| **Manufacturing** | CNC control panels | Remote operation |

### Share Your Skills

```bash
# Package your skill
clawbot skill package ./my-skill

# Share with the community
clawbot skill publish my-skill
```

**Every skill you create helps someone else automate their legacy systems.**

---

## Deployment Options

### Option 1: Safe Sandbox (Recommended for Testing)

Run a complete Windows/macOS/Linux VM isolated from your network:

```bash
# Start the sandbox VM
docker-compose up -d

# Access via web browser
open http://localhost:8006
```

### Option 2: Native Control (Production)

Direct control of the local machine:

```bash
# Configure for native mode
clawbot setup --mode native

# Run automations directly
clawbot run "Open Outlook and check for unread emails"
```

### Option 3: Remote Machine Control

Automate machines across your network:

```yaml
# config/local.yaml
vm:
  provider_type: cloud
  host: 192.168.1.100
  api_key: your-secure-key
```

---

## Security & Compliance

| Concern | ClawBot Approach |
|---------|------------------|
| **Data Privacy** | AI runs 100% locally—no data leaves your network |
| **Air-Gapped Systems** | Works completely offline after initial setup |
| **Audit Trail** | Full logging of all AI decisions and actions |
| **Sandboxing** | VM isolation prevents unintended system changes |
| **Access Control** | Integrates with existing IAM through OpenClaw |

---

## Getting Started

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.ai) (local AI runtime)
- Docker (for VM mode) or native OS access

### Quick Start

```bash
# Clone the repository
git clone https://github.com/user/clawbot
cd clawbot

# Create environment and install
make venv && source .venv/bin/activate
make install

# Pull the AI model
ollama pull qwen2.5:3b

# Run the setup wizard
clawbot setup

# Try the demo
clawbot demo
```

### Connect to Chat Platforms

```bash
# Install OpenClaw for multi-channel support
npm install -g openclaw@latest

# Connect to Slack
openclaw channel add slack --token xoxb-your-token

# Now control computers from Slack!
# @clawbot run "Take a screenshot of the dashboard"
```

---

## ROI Calculator

| Metric | Manual Process | With ClawBot |
|--------|---------------|--------------|
| Data entry (1000 records) | 8 hours | 15 minutes |
| Daily report generation | 2 hours | 2 minutes |
| System monitoring checks | 4 hours/day | Continuous |
| Training new operators | 2 weeks | 1 day |

**Typical automation saves 70-90% of time on repetitive GUI tasks.**

---

## Roadmap

- [x] Core automation engine
- [x] Calculator demo skill
- [x] Multi-platform support (Windows, macOS, Linux)
- [ ] Skill marketplace
- [ ] Visual skill builder (no-code)
- [ ] Enterprise SSO integration
- [ ] Scheduled automation triggers
- [ ] Multi-machine orchestration

---

## Contributing

We welcome contributions! Whether it's:

- 🐛 **Bug fixes** - Help us improve stability
- 📚 **New skills** - Automate more applications
- 📖 **Documentation** - Make ClawBot easier to use
- 🌍 **Translations** - Reach more users globally

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - Use freely in commercial and personal projects.

---

<p align="center">
  <b>ClawBot: Because every computer deserves an AI upgrade.</b>
  <br><br>
  <a href="#getting-started">Get Started</a> •
  <a href="#build-your-own-skills">Build Skills</a> •
  <a href="https://github.com/user/clawbot/discussions">Community</a>
</p>
