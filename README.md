# ClawBot

AI-powered Windows automation with OpenClaw + Cua.

Control Windows applications through natural language using local AI models (Ollama).

## Features

- **Natural Language Control**: Tell the AI what you want to do in plain English
- **Two Deployment Modes**:
  - **VM Mode**: Safe sandbox using Docker + QEMU Windows 11
  - **Native Mode**: Direct Windows control via pyautogui
- **Local AI**: Runs entirely on your machine with Ollama (no cloud dependencies)
- **OpenClaw Integration**: Use as a skill in the OpenClaw gateway

## Quick Start

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.ai) with `qwen2.5:3b` model
- Docker (for VM mode) or Windows (for native mode)

### Installation

```bash
# Clone the repository
git clone https://github.com/user/clawbot
cd clawbot

# Create virtual environment and install
make venv
source .venv/bin/activate
make install

# Pull the AI model
ollama pull qwen2.5:3b

# Run the setup wizard
clawbot setup
```

### Usage

```bash
# Run the Calculator demo
clawbot demo

# Execute AI tasks
clawbot run "Open Calculator and compute 15 * 8"

# Direct commands
clawbot launch Calculator
clawbot click 500 300
clawbot type "Hello, World!"
clawbot hotkey ctrl c
```

## Commands

| Command | Description |
|---------|-------------|
| `clawbot setup` | Interactive setup wizard |
| `clawbot demo` | Run the Calculator demo |
| `clawbot run "task"` | Execute an AI-controlled task |
| `clawbot screenshot` | Capture screen |
| `clawbot click X Y` | Click at coordinates |
| `clawbot type "text"` | Type text |
| `clawbot launch APP` | Launch application |
| `clawbot press KEY` | Press keyboard key |
| `clawbot hotkey K1 K2` | Press key combination |
| `clawbot config` | Show configuration |
| `clawbot status` | Check dependencies |

## Configuration

Configuration is stored in `config/local.yaml`:

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

Override with environment variables:

```bash
export CLAWBOT_DEPLOYMENT__MODE=native
export CLAWBOT_MODEL__NAME=llama3.2-vision:11b
```

## VM Mode (Docker)

Start the Windows VM:

```bash
make vm-up
```

Access via:
- **noVNC**: http://localhost:8006
- **VNC**: localhost:5900
- **RDP**: localhost:3389

Stop the VM:

```bash
make vm-down
```

## Native Mode (Windows)

Install native dependencies:

```bash
make install-native
```

Run on Windows directly - no VM needed.

## Development

```bash
# Install dev dependencies
make install

# Run tests
make test

# Lint code
make lint

# Format code
make format
```

## OpenClaw Integration

Install the skill:

```bash
clawbot setup  # Select "Install computer-use skill"
```

Use via OpenClaw:

```
openclaw
> Use computer-use to open Notepad and type "Hello from AI"
```

## Architecture

```
User Input → ClawBot CLI → Cua Bridge → Computer Control
                ↓
           AI Agent (Ollama) → Screen Analysis → Actions
```

## License

MIT
