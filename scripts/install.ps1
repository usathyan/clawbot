# DeskPilot Installer for Windows
# Usage: irm https://raw.githubusercontent.com/usathyan/deskpilot/main/scripts/install.ps1 | iex

param(
    [switch]$SkipOllama,
    [switch]$SkipOpenClaw,
    [string]$Model = "qwen2.5:3b",
    [switch]$Dev
)

$ErrorActionPreference = "Stop"

# Colors
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) { Write-Output $args }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Blue
Write-Host "                    DeskPilot Installer                         " -ForegroundColor Blue
Write-Host "            AI-Powered Desktop Automation                       " -ForegroundColor Blue
Write-Host "=================================================================" -ForegroundColor Blue
Write-Host ""

# Check Python
function Test-Python {
    Write-Host "Checking Python..." -ForegroundColor Blue

    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]

            if ($major -ge 3 -and $minor -ge 11) {
                Write-Host "  [OK] Python $major.$minor found" -ForegroundColor Green
                return $true
            } else {
                Write-Host "  [!] Python 3.11+ required (found $major.$minor)" -ForegroundColor Yellow
                return $false
            }
        }
    } catch {
        Write-Host "  [X] Python not found" -ForegroundColor Red
        return $false
    }
    return $false
}

# Check/Install Ollama
function Test-Ollama {
    Write-Host "Checking Ollama..." -ForegroundColor Blue

    try {
        $null = Get-Command ollama -ErrorAction Stop
        Write-Host "  [OK] Ollama found" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  [!] Ollama not found" -ForegroundColor Yellow
        return $false
    }
}

function Install-Ollama {
    Write-Host "Installing Ollama..." -ForegroundColor Blue

    # Download Ollama installer
    $installerUrl = "https://ollama.ai/download/OllamaSetup.exe"
    $installerPath = "$env:TEMP\OllamaSetup.exe"

    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
    Start-Process -FilePath $installerPath -Wait

    Write-Host "  [OK] Ollama installed" -ForegroundColor Green
}

# Pull AI model
function Install-Model {
    param([string]$ModelName)

    Write-Host "Pulling AI model ($ModelName)..." -ForegroundColor Blue

    # Start Ollama if not running
    $ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
    if (-not $ollamaProcess) {
        Write-Host "  Starting Ollama service..."
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3
    }

    & ollama pull $ModelName
    Write-Host "  [OK] Model $ModelName ready" -ForegroundColor Green
}

# Check Node.js
function Test-Node {
    Write-Host "Checking Node.js..." -ForegroundColor Blue

    try {
        $nodeVersion = node -v 2>&1
        if ($nodeVersion -match "v(\d+)") {
            $major = [int]$Matches[1]
            if ($major -ge 18) {
                Write-Host "  [OK] Node.js v$major found" -ForegroundColor Green
                return $true
            } else {
                Write-Host "  [!] Node.js 18+ required (found v$major)" -ForegroundColor Yellow
                return $false
            }
        }
    } catch {
        Write-Host "  [!] Node.js not found" -ForegroundColor Yellow
        return $false
    }
    return $false
}

# Install OpenClaw
function Install-OpenClaw {
    Write-Host "Installing OpenClaw..." -ForegroundColor Blue

    try {
        npm install -g openclaw@latest
        Write-Host "  [OK] OpenClaw installed" -ForegroundColor Green
    } catch {
        Write-Host "  [X] Failed to install OpenClaw" -ForegroundColor Red
    }
}

# Install DeskPilot
function Install-DeskPilot {
    param([switch]$DevMode)

    Write-Host "Installing DeskPilot..." -ForegroundColor Blue

    if ($DevMode) {
        if (Test-Path "pyproject.toml") {
            pip install -e ".[dev]"
            Write-Host "  [OK] DeskPilot installed (dev mode)" -ForegroundColor Green
        } else {
            Write-Host "  [X] pyproject.toml not found" -ForegroundColor Red
        }
    } else {
        pip install deskpilot
        Write-Host "  [OK] DeskPilot installed" -ForegroundColor Green
    }
}

# Install skill
function Install-Skill {
    Write-Host "Installing computer-use skill..." -ForegroundColor Blue

    $skillSrc = ".\src\deskpilot\openclaw_skill\computer-use"
    $skillDest = "$env:USERPROFILE\.openclaw\skills\computer-use"

    if (Test-Path $skillSrc) {
        New-Item -ItemType Directory -Path (Split-Path $skillDest) -Force | Out-Null
        Copy-Item -Path $skillSrc -Destination $skillDest -Recurse -Force
        Write-Host "  [OK] Skill installed to $skillDest" -ForegroundColor Green
    } else {
        Write-Host "  [!] Skill source not found - skipping" -ForegroundColor Yellow
    }
}

# Initialize agent configuration
function Initialize-AgentConfig {
    Write-Host "Initializing agent configuration..." -ForegroundColor Blue

    $configDir = "$env:USERPROFILE\.openclaw\skills\computer-use"

    if (Test-Path $configDir) {
        $userMd = "$configDir\USER.md"
        if (Test-Path $userMd) {
            $content = Get-Content $userMd -Raw
            if ($content -match "\[Your name\]") {
                Write-Host "  [!] USER.md needs personalization" -ForegroundColor Yellow
                Write-Host "      Edit: $userMd" -ForegroundColor Yellow
            } else {
                Write-Host "  [OK] USER.md configured" -ForegroundColor Green
            }
        }

        Write-Host "  Agent configuration files:" -ForegroundColor Blue
        Write-Host "    - SOUL.md      How the agent communicates"
        Write-Host "    - USER.md      Your context (EDIT THIS FIRST)"
        Write-Host "    - MEMORY.md    Persistent knowledge"
        Write-Host "    - HEARTBEAT.md Proactive monitoring"
        Write-Host "    - CRON.md      Scheduled automation"
    }
}

# Smoke test
function Test-Installation {
    Write-Host "Running smoke test..." -ForegroundColor Blue

    try {
        $version = deskpilot --version 2>&1
        Write-Host "  [OK] DeskPilot CLI working" -ForegroundColor Green
    } catch {
        Write-Host "  [!] DeskPilot CLI not responding" -ForegroundColor Yellow
    }

    try {
        $models = ollama list 2>&1
        Write-Host "  [OK] Ollama service working" -ForegroundColor Green
    } catch {
        Write-Host "  [!] Ollama service not responding" -ForegroundColor Yellow
    }
}

# Main
Write-Host "Installation options:"
Write-Host "  Skip Ollama: $SkipOllama"
Write-Host "  Skip OpenClaw: $SkipOpenClaw"
Write-Host "  Model: $Model"
Write-Host "  Dev mode: $Dev"
Write-Host ""

# Check Python
if (-not (Test-Python)) {
    Write-Host "Please install Python 3.11+ and try again" -ForegroundColor Red
    exit 1
}

# Install Ollama
if (-not $SkipOllama) {
    if (-not (Test-Ollama)) {
        Install-Ollama
    }
    Install-Model -ModelName $Model
}

# Install OpenClaw
if (-not $SkipOpenClaw) {
    if (Test-Node) {
        Install-OpenClaw
    } else {
        Write-Host "Skipping OpenClaw (Node.js 18+ required)" -ForegroundColor Yellow
    }
}

# Install DeskPilot
Install-DeskPilot -DevMode:$Dev

# Install skill
Install-Skill

# Initialize agent config
Initialize-AgentConfig

# Smoke test
Write-Host ""
Test-Installation

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "                   Installation Complete!                       " -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host ""
Write-Host "  1. IMPORTANT: Configure your agent" -ForegroundColor Yellow
Write-Host "     Edit $env:USERPROFILE\.openclaw\skills\computer-use\USER.md"
Write-Host "     Fill in your context, workflows, and preferences"
Write-Host ""
Write-Host "  2. Start Ollama: ollama serve"
Write-Host "  3. Launch TUI:   openclaw dashboard"
Write-Host "  4. Or run demo:  deskpilot demo"
Write-Host ""
Write-Host "Configuration files:"
Write-Host "  $env:USERPROFILE\.openclaw\skills\computer-use\SOUL.md      - Agent personality"
Write-Host "  $env:USERPROFILE\.openclaw\skills\computer-use\USER.md      - YOUR context"
Write-Host "  $env:USERPROFILE\.openclaw\skills\computer-use\MEMORY.md    - Persistent memory"
Write-Host "  $env:USERPROFILE\.openclaw\skills\computer-use\HEARTBEAT.md - Monitoring"
Write-Host "  $env:USERPROFILE\.openclaw\skills\computer-use\CRON.md      - Scheduled tasks"
Write-Host ""
