# DeskPilot TUI Auto-Start Script
# This script runs on Windows login to start the OpenClaw TUI

$ErrorActionPreference = "SilentlyContinue"

# Wait for desktop to be ready
Start-Sleep -Seconds 5

# Start Ollama if not running
$ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
if (-not $ollamaProcess) {
    Start-Process -FilePath "C:\Program Files\Ollama\ollama.exe" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

# Launch OpenClaw TUI in a new terminal window
$welcomeMessage = @"
================================================================================
                         DeskPilot Demo Environment
================================================================================

Welcome! This is a self-contained demo of DeskPilot.

Try these commands:
  > Open Calculator and compute 15 * 8
  > Take a screenshot
  > Click on the Start button

Type 'exit' to close the TUI.

================================================================================
"@

# Create a temp script that shows welcome and starts TUI
$tuiScript = @"
Clear-Host
Write-Host '$welcomeMessage'
openclaw dashboard
"@

$tuiScriptPath = "$env:TEMP\start-tui.ps1"
$tuiScript | Out-File -FilePath $tuiScriptPath -Encoding UTF8

# Start the TUI in a visible terminal
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $tuiScriptPath
