---
name: computer-use
description: Control Windows applications through AI-powered automation using ClawBot
version: 0.1.0
author: ClawBot
tags:
  - automation
  - windows
  - computer-use
  - ai
---

# Computer Use Skill

Control Windows desktop applications through natural language commands using ClawBot.

## Prerequisites

- ClawBot installed and configured (`clawbot setup`)
- Ollama running with qwen2.5:3b model
- Either VM mode (Docker) or Native mode (Windows) configured

## Commands

### Screenshot

Capture the current screen state:

```bash
clawbot screenshot --save
clawbot screenshot --describe  # Get AI description
```

### Click

Click at coordinates or on elements:

```bash
clawbot click 500 300              # Click at x=500, y=300
clawbot click 500 300 --double     # Double-click
clawbot click --button right       # Right-click
```

### Type

Type text into the focused element:

```bash
clawbot type "Hello, World!"
clawbot type "user@example.com"
```

### Launch

Launch an application:

```bash
clawbot launch Calculator
clawbot launch Notepad
clawbot launch "Microsoft Edge"
```

### Press Key

Press a single key:

```bash
clawbot press enter
clawbot press escape
clawbot press tab
```

### Hotkey

Press a key combination:

```bash
clawbot hotkey ctrl c        # Copy
clawbot hotkey ctrl v        # Paste
clawbot hotkey alt f4        # Close window
clawbot hotkey ctrl shift s  # Save as
```

### Run Task

Execute an AI-controlled task with natural language:

```bash
clawbot run "Open Calculator and compute 15 * 8"
clawbot run "Find and click the Settings button"
clawbot run "Type 'Hello' in the search box and press Enter"
```

## Example Workflows

### Calculator Workflow

```bash
# Launch Calculator
clawbot launch Calculator

# Wait for it to open
sleep 2

# Compute 15 * 8
clawbot run "Click the buttons to compute 15 times 8"

# Or use direct commands
clawbot type "15*8"
clawbot press enter
```

### File Operations

```bash
# Open File Explorer
clawbot hotkey win e

# Navigate and create folder
clawbot run "Navigate to Documents and create a new folder called 'Test'"
```

### Web Automation

```bash
# Open browser
clawbot launch "Microsoft Edge"

# Navigate to URL
clawbot run "Go to github.com and search for ClawBot"
```

## Interactive Demo

Run the interactive calculator demo:

```bash
clawbot demo
```

This launches Calculator and lets you enter calculations that the AI performs.

## Configuration

View current configuration:

```bash
clawbot config
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
clawbot screenshot --mock  # Test with mock mode
```

## Integration with OpenClaw

When installed as an OpenClaw skill, you can use it via the gateway:

```
openclaw
> Use computer-use to open Calculator and compute 100 / 4
```

The skill will automatically:
1. Parse your request
2. Execute the appropriate clawbot commands
3. Return the results

## API Reference

All commands support `--mock` flag for testing without actual computer control:

```bash
clawbot screenshot --mock
clawbot click 100 100 --mock
clawbot run "test task" --mock
```

Check dependencies:

```bash
clawbot status
```
