---
name: computer-use
description: Control Windows applications through AI-powered automation using DeskPilot
version: 0.1.0
author: DeskPilot
tags:
  - automation
  - windows
  - computer-use
  - ai
---

# Computer Use Skill

Control Windows desktop applications through natural language commands using DeskPilot.

## Prerequisites

- DeskPilot installed and configured (`deskpilot setup`)
- Ollama running with qwen2.5:3b model
- Either VM mode (Docker) or Native mode (Windows) configured

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

# Compute 15 * 8
deskpilot run "Click the buttons to compute 15 times 8"

# Or use direct commands
deskpilot type "15*8"
deskpilot press enter
```

### File Operations

```bash
# Open File Explorer
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
deployment:
  mode: vm  # or 'native'

model:
  provider: ollama
  name: qwen2.5:3b

agent:
  max_steps: 50
  verbose: true
```

## Troubleshooting

### VM not starting
```bash
# Check Docker status
docker ps

# Start VM
make vm-up

# View logs
make vm-logs
```

### Ollama not responding
```bash
# Check Ollama status
ollama list

# Pull model if missing
ollama pull qwen2.5:3b
```

### Screenshots not working
```bash
# Check screen capture permissions (macOS/Linux)
# On Windows, run as administrator if needed
deskpilot screenshot --mock  # Test with mock mode
```

## Integration with OpenClaw

When installed as an OpenClaw skill, you can use it via the gateway:

```
openclaw
> Use computer-use to open Calculator and compute 100 / 4
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

Check dependencies:

```bash
deskpilot status
```
