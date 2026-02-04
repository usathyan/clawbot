#!/bin/bash
# DeskPilot Installer for macOS/Linux
# Usage: curl -fsSL https://raw.githubusercontent.com/usathyan/deskpilot/main/scripts/install.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                     DeskPilot Installer                        ║"
echo "║           AI-Powered Desktop Automation                        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Detect OS
OS="$(uname -s)"
ARCH="$(uname -m)"

echo -e "${BLUE}Detected:${NC} $OS ($ARCH)"
echo ""

# Check Python version
check_python() {
    echo -e "${BLUE}Checking Python...${NC}"

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
        MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 11 ]; then
            echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION found"
            return 0
        else
            echo -e "  ${RED}✗${NC} Python 3.11+ required (found $PYTHON_VERSION)"
            return 1
        fi
    else
        echo -e "  ${RED}✗${NC} Python not found"
        return 1
    fi
}

# Check/Install Ollama
check_ollama() {
    echo -e "${BLUE}Checking Ollama...${NC}"

    if command -v ollama &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Ollama found"
        return 0
    else
        echo -e "  ${YELLOW}!${NC} Ollama not found"
        return 1
    fi
}

install_ollama() {
    echo -e "${BLUE}Installing Ollama...${NC}"

    if [ "$OS" = "Darwin" ]; then
        if command -v brew &> /dev/null; then
            brew install ollama
        else
            curl -fsSL https://ollama.ai/install.sh | sh
        fi
    else
        curl -fsSL https://ollama.ai/install.sh | sh
    fi

    echo -e "  ${GREEN}✓${NC} Ollama installed"
}

# Pull AI model
pull_model() {
    local MODEL="${1:-qwen2.5:3b}"
    echo -e "${BLUE}Pulling AI model ($MODEL)...${NC}"

    # Start Ollama if not running
    if ! pgrep -x "ollama" > /dev/null; then
        echo -e "  Starting Ollama service..."
        ollama serve &> /dev/null &
        sleep 3
    fi

    ollama pull "$MODEL"
    echo -e "  ${GREEN}✓${NC} Model $MODEL ready"
}

# Check/Install Node.js for OpenClaw
check_node() {
    echo -e "${BLUE}Checking Node.js...${NC}"

    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$NODE_VERSION" -ge 18 ]; then
            echo -e "  ${GREEN}✓${NC} Node.js v$NODE_VERSION found"
            return 0
        else
            echo -e "  ${YELLOW}!${NC} Node.js 18+ required (found v$NODE_VERSION)"
            return 1
        fi
    else
        echo -e "  ${YELLOW}!${NC} Node.js not found"
        return 1
    fi
}

# Install OpenClaw
install_openclaw() {
    echo -e "${BLUE}Installing OpenClaw...${NC}"

    if command -v npm &> /dev/null; then
        npm install -g openclaw@latest
        echo -e "  ${GREEN}✓${NC} OpenClaw installed"
    else
        echo -e "  ${RED}✗${NC} npm not found - skipping OpenClaw"
        return 1
    fi
}

# Install DeskPilot via pip
install_deskpilot() {
    echo -e "${BLUE}Installing DeskPilot...${NC}"

    if command -v uv &> /dev/null; then
        uv pip install deskpilot
    elif command -v pip3 &> /dev/null; then
        pip3 install deskpilot
    else
        echo -e "  ${RED}✗${NC} pip not found"
        return 1
    fi

    echo -e "  ${GREEN}✓${NC} DeskPilot installed"
}

# Install DeskPilot from source (development mode)
install_deskpilot_dev() {
    echo -e "${BLUE}Installing DeskPilot (development mode)...${NC}"

    if [ -f "pyproject.toml" ]; then
        if command -v uv &> /dev/null; then
            uv pip install -e ".[dev]"
        else
            pip3 install -e ".[dev]"
        fi
        echo -e "  ${GREEN}✓${NC} DeskPilot installed (dev mode)"
    else
        echo -e "  ${RED}✗${NC} pyproject.toml not found - run from project root"
        return 1
    fi
}

# Install computer-use skill
install_skill() {
    echo -e "${BLUE}Installing computer-use skill...${NC}"

    SKILL_SRC="./src/deskpilot/openclaw_skill/computer-use"
    SKILL_DEST="$HOME/.openclaw/skills/computer-use"

    if [ -d "$SKILL_SRC" ]; then
        mkdir -p "$(dirname "$SKILL_DEST")"
        cp -r "$SKILL_SRC" "$SKILL_DEST"
        echo -e "  ${GREEN}✓${NC} Skill installed to $SKILL_DEST"
    else
        echo -e "  ${YELLOW}!${NC} Skill source not found - skipping"
    fi
}

# Initialize agent configuration files
init_agent_config() {
    echo -e "${BLUE}Initializing agent configuration...${NC}"

    CONFIG_DIR="$HOME/.openclaw/skills/computer-use"

    if [ -d "$CONFIG_DIR" ]; then
        # Check if USER.md has been personalized (not just template)
        if [ -f "$CONFIG_DIR/USER.md" ]; then
            if grep -q "\[Your name\]" "$CONFIG_DIR/USER.md"; then
                echo -e "  ${YELLOW}!${NC} USER.md needs personalization"
                echo -e "     Edit: $CONFIG_DIR/USER.md"
            else
                echo -e "  ${GREEN}✓${NC} USER.md configured"
            fi
        fi

        # List all config files
        echo -e "  Agent configuration files:"
        echo -e "    - ${BLUE}SOUL.md${NC}      How the agent communicates"
        echo -e "    - ${BLUE}USER.md${NC}      Your context (EDIT THIS FIRST)"
        echo -e "    - ${BLUE}MEMORY.md${NC}    Persistent knowledge"
        echo -e "    - ${BLUE}HEARTBEAT.md${NC} Proactive monitoring"
        echo -e "    - ${BLUE}CRON.md${NC}      Scheduled automation"
    fi
}

# Run smoke test
smoke_test() {
    echo -e "${BLUE}Running smoke test...${NC}"

    if command -v deskpilot &> /dev/null; then
        if deskpilot --version &> /dev/null; then
            echo -e "  ${GREEN}✓${NC} DeskPilot CLI working"
        else
            echo -e "  ${RED}✗${NC} DeskPilot CLI failed"
            return 1
        fi
    else
        echo -e "  ${YELLOW}!${NC} deskpilot command not in PATH"
    fi

    if command -v ollama &> /dev/null; then
        if ollama list &> /dev/null; then
            echo -e "  ${GREEN}✓${NC} Ollama service working"
        else
            echo -e "  ${YELLOW}!${NC} Ollama service not responding"
        fi
    fi
}

# Main installation flow
main() {
    local SKIP_OLLAMA=false
    local SKIP_OPENCLAW=false
    local MODEL="qwen2.5:3b"
    local DEV_MODE=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-ollama)
                SKIP_OLLAMA=true
                shift
                ;;
            --skip-openclaw)
                SKIP_OPENCLAW=true
                shift
                ;;
            --model)
                MODEL="$2"
                shift 2
                ;;
            --dev)
                DEV_MODE=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    echo "Installation options:"
    echo "  Skip Ollama: $SKIP_OLLAMA"
    echo "  Skip OpenClaw: $SKIP_OPENCLAW"
    echo "  Model: $MODEL"
    echo "  Dev mode: $DEV_MODE"
    echo ""

    # Check requirements
    if ! check_python; then
        echo -e "${RED}Please install Python 3.11+ and try again${NC}"
        exit 1
    fi

    # Install Ollama
    if [ "$SKIP_OLLAMA" = false ]; then
        if ! check_ollama; then
            install_ollama
        fi
        pull_model "$MODEL"
    fi

    # Install OpenClaw
    if [ "$SKIP_OPENCLAW" = false ]; then
        if check_node; then
            install_openclaw
        else
            echo -e "${YELLOW}Skipping OpenClaw (Node.js 18+ required)${NC}"
        fi
    fi

    # Install DeskPilot
    if [ "$DEV_MODE" = true ]; then
        install_deskpilot_dev
    else
        install_deskpilot
    fi

    # Install skill
    install_skill

    # Initialize agent config
    init_agent_config

    # Smoke test
    echo ""
    smoke_test

    echo ""
    echo -e "${GREEN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                   Installation Complete!                       ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo "Next steps:"
    echo ""
    echo "  ${YELLOW}1. IMPORTANT: Configure your agent${NC}"
    echo "     Edit ~/.openclaw/skills/computer-use/USER.md"
    echo "     Fill in your context, workflows, and preferences"
    echo ""
    echo "  2. Start Ollama: ollama serve"
    echo "  3. Launch TUI:   openclaw dashboard"
    echo "  4. Or run demo:  deskpilot demo"
    echo ""
    echo "Configuration files:"
    echo "  ~/.openclaw/skills/computer-use/SOUL.md      - Agent personality"
    echo "  ~/.openclaw/skills/computer-use/USER.md      - YOUR context"
    echo "  ~/.openclaw/skills/computer-use/MEMORY.md    - Persistent memory"
    echo "  ~/.openclaw/skills/computer-use/HEARTBEAT.md - Monitoring"
    echo "  ~/.openclaw/skills/computer-use/CRON.md      - Scheduled tasks"
    echo ""
}

main "$@"
