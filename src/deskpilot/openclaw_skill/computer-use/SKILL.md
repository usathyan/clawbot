---
name: computer-use
description: Control desktop applications through AI-powered automation using DeskPilot
version: 0.3.0
author: DeskPilot
tags:
  - automation
  - desktop
  - computer-use
  - ai
---

# Computer Use Skill

Control any desktop application through natural language commands using DeskPilot.

## Agent Configuration Files

This skill uses a multi-file configuration pattern for personalized automation:

| File | Purpose |
|------|---------|
| **SOUL.md** | How the agent thinks and communicates |
| **USER.md** | Who the agent is working for (your context) |
| **MEMORY.md** | What the agent retains across sessions |
| **HEARTBEAT.md** | Proactive monitoring configuration |
| **CRON.md** | Scheduled task automation |

**Setup Priority:**
1. Start with **USER.md** - fill in your context, workflows, and preferences
2. Review **SOUL.md** - adjust communication style if needed
3. Configure **HEARTBEAT.md** - enable monitors that matter to you
4. Set up **CRON.md** - define scheduled automation tasks
5. **MEMORY.md** updates automatically as you work

> **Tip:** Spend 5-10 minutes configuring USER.md properly. The more context you provide, the more relevant the automation becomes. Use voice transcription to quickly describe your workflows.

## Prerequisites

- DeskPilot installed (`pip install deskpilot` or `deskpilot install`)
- Ollama running with qwen2.5:3b model (`ollama serve`)
- Native packages installed (pyautogui, mss, pillow)

## Quick Start

```bash
# Check everything is ready
deskpilot status

# Run the Calculator demo
deskpilot demo

# Or launch the interactive TUI
deskpilot tui
```

## Commands

### Screenshot

Capture the current screen state:

```bash
deskpilot screenshot --save
deskpilot screenshot --describe  # Get AI description
```

### Click

Click at coordinates or on elements:

```bash
deskpilot click 500 300              # Click at x=500, y=300
deskpilot click 500 300 --double     # Double-click
deskpilot click --button right       # Right-click
```

### Type

Type text into the focused element:

```bash
deskpilot type "Hello, World!"
deskpilot type "user@example.com"
```

### Launch

Launch an application:

```bash
deskpilot launch Calculator
deskpilot launch Notepad
deskpilot launch "Microsoft Edge"
```

### Press Key

Press a single key:

```bash
deskpilot press enter
deskpilot press escape
deskpilot press tab
```

### Hotkey

Press a key combination:

```bash
deskpilot hotkey ctrl c        # Copy
deskpilot hotkey ctrl v        # Paste
deskpilot hotkey alt f4        # Close window
deskpilot hotkey ctrl shift s  # Save as
```

### Run Task

Execute an AI-controlled task with natural language:

```bash
deskpilot run "Open Calculator and compute 15 * 8"
deskpilot run "Find and click the Settings button"
deskpilot run "Type 'Hello' in the search box and press Enter"
```

## Example Workflows

### Calculator Workflow

```bash
# Launch Calculator
deskpilot launch Calculator

# Wait for it to open
sleep 2

# Compute 15 * 8 using AI
deskpilot run "Click the buttons to compute 15 times 8"

# Or use direct commands
deskpilot type "15*8"
deskpilot press enter
```

### File Operations

```bash
# Open File Explorer (Windows)
deskpilot hotkey win e

# Navigate and create folder
deskpilot run "Navigate to Documents and create a new folder called 'Test'"
```

### Web Automation

```bash
# Open browser
deskpilot launch "Microsoft Edge"

# Navigate to URL
deskpilot run "Go to github.com and search for DeskPilot"
```

## Interactive Demo

Run the interactive calculator demo:

```bash
deskpilot demo
```

This launches Calculator and lets you enter calculations that the AI performs.

## Configuration

View current configuration:

```bash
deskpilot config
```

Key settings in `config/local.yaml`:

```yaml
model:
  provider: ollama
  name: qwen2.5:3b

agent:
  max_steps: 50
  verbose: true

native:
  typing_interval: 0.05
  click_pause: 0.1
```

## Troubleshooting

### Ollama not responding
```bash
# Check Ollama status
ollama list

# Start Ollama service
ollama serve

# Pull model if missing
ollama pull qwen2.5:3b
```

### Screenshots not working
```bash
# On macOS: Grant screen recording permission in System Preferences
# On Windows: Run as administrator if needed

# Test with mock mode
deskpilot screenshot --mock
```

### Click not working
```bash
# On macOS: Grant accessibility permission
# System Preferences > Security & Privacy > Privacy > Accessibility

# Test with mock mode
deskpilot click 100 100 --mock
```

## Integration with OpenClaw TUI

When installed as an OpenClaw skill, you can use it via the TUI:

```bash
# Launch the TUI
deskpilot tui
# or
openclaw dashboard

# Then type commands like:
> Open Calculator and compute 100 / 4
> Take a screenshot of the desktop
> Click on the Start button
```

The skill will automatically:
1. Parse your request
2. Execute the appropriate deskpilot commands
3. Return the results

## API Reference

All commands support `--mock` flag for testing without actual computer control:

```bash
deskpilot screenshot --mock
deskpilot click 100 100 --mock
deskpilot run "test task" --mock
```

Check dependencies and status:

```bash
deskpilot status
```

## Agent Personalization

### Configuring Your Agent

The files in this skill directory work together:

```
computer-use/
├── SKILL.md      # This file (commands and usage)
├── SOUL.md       # Agent personality and boundaries
├── USER.md       # Your context and preferences
├── MEMORY.md     # Persistent knowledge
├── HEARTBEAT.md  # Proactive monitoring
└── CRON.md       # Scheduled automation
```

### Quick Configuration Checklist

**USER.md (Required):**
- [ ] Basic info (name, timezone, OS)
- [ ] Current projects and priorities
- [ ] Primary applications you use
- [ ] Common workflows to automate
- [ ] Communication preferences
- [ ] Boundaries (sensitive apps, off-limits areas)

**SOUL.md (Optional tweaks):**
- [ ] Adjust communication style
- [ ] Modify autonomy levels
- [ ] Update error handling preferences

**HEARTBEAT.md (Enable as needed):**
- [ ] System health monitoring
- [ ] Application state checks
- [ ] Workflow-specific monitors

**CRON.md (Enable as needed):**
- [ ] Morning startup routine
- [ ] End of day cleanup
- [ ] Weekly maintenance

### Maintenance Habits

**Daily (5 min):**
- Update USER.md with priority changes
- Review MEMORY.md session log

**Weekly (15 min):**
- Archive old memory entries
- Review heartbeat/cron effectiveness
- Update project context

### Example USER.md for Developer

```yaml
# Basic Info
Name: Alex
Timezone: America/Los_Angeles
OS: macOS Sonoma

# Work Context
Role: Backend Engineer at TechCo
Projects:
  - [HIGH] API migration - due Feb 15
  - [MEDIUM] Code review backlog

# Primary Apps
- VS Code (Python, Docker extensions)
- Chrome (GitHub, Jira, Slack web)
- Terminal (zsh, kubectl, docker)

# Workflows
Morning: Open VS Code + Chrome + Slack, check Jira board
PR Review: Pull branch, run tests, comment on GitHub

# Preferences
Communication: Technical, precise
Confirmations: Only for destructive actions
Boundaries: Never access ~/private or banking apps
```

### Example CRON for Developer

```yaml
# Morning startup at 9 AM weekdays
task: dev_morning
schedule: "0 9 * * 1-5"
actions:
  - launch: "VS Code"
  - launch: "Chrome"
  - execute: "open https://jira.company.com/board"
```

## Best Practices

1. **Start conservative** - Enable few automations, add more as you trust the system
2. **Test with --mock** - Always test new workflows in mock mode first
3. **Review memory weekly** - Keep corrections current, archive stale entries
4. **Iterate on USER.md** - The more context, the better results
5. **Use heartbeat wisely** - Too many monitors = notification fatigue
