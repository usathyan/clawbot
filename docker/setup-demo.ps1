# DeskPilot Demo Setup Script
# This script runs inside the Windows VM to set up the demo environment
# It uses the same install.ps1 script used for native installation to ensure consistency

$ErrorActionPreference = "Stop"
$SetupLog = "C:\DeskPilot\setup.log"

# Create directories
New-Item -ItemType Directory -Path "C:\DeskPilot" -Force | Out-Null
Start-Transcript -Path $SetupLog

Write-Host "=========================================="
Write-Host "    DeskPilot Demo Environment Setup"
Write-Host "=========================================="
Write-Host ""

# -------------------------------------------
# Pre-requisites: Install Python and Node.js
# (Required before running install.ps1)
# -------------------------------------------

Write-Host "[1/4] Installing Python..."

$pythonUrl = "https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
$pythonInstaller = "C:\DeskPilot\python-installer.exe"

Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait

# Refresh PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

Write-Host "  [OK] Python installed"

# -------------------------------------------
Write-Host "[2/4] Installing Node.js..."

$nodeUrl = "https://nodejs.org/dist/v20.10.0/node-v20.10.0-x64.msi"
$nodeInstaller = "C:\DeskPilot\node-installer.msi"

Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeInstaller
Start-Process -FilePath "msiexec.exe" -ArgumentList "/i", $nodeInstaller, "/quiet", "/norestart" -Wait

# Refresh PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

Write-Host "  [OK] Node.js installed"

# -------------------------------------------
# Copy DeskPilot source to local directory
# -------------------------------------------
Write-Host "[3/4] Preparing DeskPilot source..."

if (Test-Path "Z:\setup\deskpilot") {
    Copy-Item -Path "Z:\setup\deskpilot" -Destination "C:\DeskPilot\src" -Recurse
    Write-Host "  [OK] DeskPilot source copied"
} else {
    Write-Host "  [!] DeskPilot source not found at Z:\setup\deskpilot"
    Write-Host "      Will install from PyPI instead"
}

# -------------------------------------------
# Run the official install.ps1 script
# This validates that our installer works correctly
# -------------------------------------------
Write-Host "[4/4] Running DeskPilot installer..."
Write-Host ""

Set-Location "C:\DeskPilot\src"

# Run the installer in dev mode (from source)
# This tests the same script users would run
if (Test-Path ".\scripts\install.ps1") {
    Write-Host "Using local install.ps1 script..."
    & powershell.exe -ExecutionPolicy Bypass -File ".\scripts\install.ps1" -Dev
} else {
    Write-Host "Using remote install.ps1 script..."
    # Fallback to remote script (tests download scenario)
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/usathyan/deskpilot/main/scripts/install.ps1'))
}

# -------------------------------------------
# Configure Auto-Start for Demo
# -------------------------------------------
Write-Host ""
Write-Host "Configuring auto-start for demo..."

# Copy autostart script to Startup folder
$startupFolder = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
Copy-Item -Path "Z:\setup\autostart-tui.ps1" -Destination "$startupFolder\deskpilot-tui.ps1" -Force

# Create desktop shortcut for OpenClaw TUI
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:PUBLIC\Desktop\DeskPilot.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -File $startupFolder\deskpilot-tui.ps1"
$Shortcut.WorkingDirectory = "$env:USERPROFILE"
$Shortcut.Description = "Launch DeskPilot TUI"
$Shortcut.Save()

# Create shortcut to agent config files
$ConfigShortcut = $WshShell.CreateShortcut("$env:PUBLIC\Desktop\DeskPilot Config.lnk")
$ConfigShortcut.TargetPath = "$env:USERPROFILE\.openclaw\skills\computer-use"
$ConfigShortcut.Description = "DeskPilot Agent Configuration Files"
$ConfigShortcut.Save()

# Pin Calculator to taskbar for demo
try {
    $shell = New-Object -ComObject shell.application
    $calc = $shell.Namespace("C:\Windows\System32").ParseName("calc.exe")
    $calc.InvokeVerb("taskbarpin")
} catch {
    Write-Host "  [!] Could not pin Calculator to taskbar"
}

Write-Host "  [OK] Auto-start configured"

# -------------------------------------------
# Display agent configuration reminder
# -------------------------------------------
Write-Host ""
Write-Host "=========================================="
Write-Host "    Demo Environment Ready!"
Write-Host "=========================================="
Write-Host ""
Write-Host "Agent configuration files:"
Write-Host "  $env:USERPROFILE\.openclaw\skills\computer-use\SOUL.md"
Write-Host "  $env:USERPROFILE\.openclaw\skills\computer-use\USER.md"
Write-Host "  $env:USERPROFILE\.openclaw\skills\computer-use\MEMORY.md"
Write-Host "  $env:USERPROFILE\.openclaw\skills\computer-use\HEARTBEAT.md"
Write-Host "  $env:USERPROFILE\.openclaw\skills\computer-use\CRON.md"
Write-Host ""
Write-Host "The OpenClaw TUI will start automatically on login."
Write-Host "You can also run: openclaw dashboard"
Write-Host ""
Write-Host "Try: 'Open Calculator and compute 15 * 8'"
Write-Host ""

Stop-Transcript
