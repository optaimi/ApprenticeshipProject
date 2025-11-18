# Product Validation System - Setup Script for Windows PowerShell
# This script automates the environment setup for development

Write-Host "=== Product Validation System Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}
Write-Host "✓ $pythonVersion" -ForegroundColor Green

# Check Node
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Node.js $nodeVersion" -ForegroundColor Green

Write-Host ""
Write-Host "Setting up Python environment..." -ForegroundColor Yellow

# Create venv
if (!(Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate venv
Write-Host "Activating virtual environment..."
& ".\.venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install Python deps
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Setting up Node.js environment..." -ForegroundColor Yellow

# Check if frontend/node_modules exists
if (!(Test-Path "frontend\node_modules")) {
    Write-Host "Installing Node.js dependencies..."
    Set-Location frontend
    npm install -q
    Set-Location ..
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Node.js dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install Node.js dependencies" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ Node.js dependencies already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Open a new PowerShell terminal for the backend:"
Write-Host "   .\.venv\Scripts\Activate.ps1"
Write-Host "   python api_server.py"
Write-Host ""
Write-Host "2. Open another PowerShell terminal for the frontend:"
Write-Host "   cd frontend"
Write-Host "   npm run dev"
Write-Host ""
Write-Host "3. Open http://localhost:3000 in your browser"
Write-Host ""
Write-Host "See QUICKSTART.md for detailed instructions and test scenarios."
