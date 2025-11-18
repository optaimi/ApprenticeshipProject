# Python Virtual Environment (venv) Guide

This guide helps you set up and manage the Python virtual environment for the Product Validation System.

## What is a Virtual Environment?

A virtual environment is an isolated Python installation on your machine. It allows you to:
- Install project dependencies without affecting your system Python
- Avoid conflicts between different project versions
- Easily reproduce the same environment on other machines

## Quick Setup

### Windows PowerShell

```powershell
# Create venv
python -m venv .venv

# Activate venv (PowerShell)
.venv\Scripts\Activate.ps1

# You should see (.venv) in your prompt
# Install dependencies (with venv active)
pip install -r requirements.txt
```

### Windows Command Prompt (CMD)

```cmd
# Create venv
python -m venv .venv

# Activate venv (CMD)
.venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

### macOS / Linux (Bash/Zsh)

```bash
# Create venv
python3 -m venv .venv

# Activate venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## How to Tell if venv is Activated?

Look at your terminal prompt:

- ✅ **Activated**: `(.venv) C:\projects\ApprenticeshipProject>`
- ❌ **Not activated**: `C:\projects\ApprenticeshipProject>`

The `(.venv)` prefix appears when the virtual environment is active.

## Deactivating venv

When you're done working:

```bash
deactivate
```

The `(.venv)` prefix will disappear from your prompt.

## Common Issues and Solutions

### ❌ "pip: command not found" or "pip is not recognized"

**Problem**: pip is not available or venv is not activated.

**Solution**:
1. Make sure venv is activated: `(.venv)` should be in your prompt
2. If not, activate it:
   ```powershell
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   ```
3. If that doesn't work, try:
   ```powershell
   python -m pip install -r requirements.txt
   ```

### ❌ "No module named 'fastapi'" or similar

**Problem**: venv is not activated, or dependencies aren't installed.

**Solution**:
1. Verify venv is activated:
   ```powershell
   (.venv) PS C:\projects\ApprenticeshipProject>
   ```
2. If not, activate it:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
3. Install/reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### ❌ "cannot be loaded because running scripts is disabled" (Windows PowerShell)

**Problem**: PowerShell script execution is disabled on your system.

**Solution - Option 1 (Temporary):**
```powershell
# Run this command once
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Solution - Option 2 (Use CMD instead):**
```cmd
# Use Command Prompt instead of PowerShell
cd C:\projects\ApprenticeshipProject
.venv\Scripts\activate.bat
```

### ❌ "python -m venv .venv" fails

**Problem**: Python is not installed or not in PATH.

**Solution**:
1. Install Python 3.10+ from python.org
2. Make sure "Add Python to PATH" is checked during installation
3. Restart your terminal
4. Try again:
   ```bash
   python --version  # Should show 3.10+
   python -m venv .venv
   ```

### ❌ "Cannot delete venv"

**Problem**: Files in venv are in use or locked.

**Solution**:
1. Deactivate venv:
   ```bash
   deactivate
   ```
2. Close the terminal window
3. Delete `.venv` folder manually in File Explorer
4. Create fresh venv:
   ```bash
   python -m venv .venv
   ```

## Recreating venv

If something goes wrong, you can always recreate it:

```powershell
# Deactivate if active
deactivate

# Delete old venv
Remove-Item -Recurse -Force .venv

# Create fresh venv
python -m venv .venv

# Activate and reinstall
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Keeping Venv Up to Date

To upgrade pip to the latest version:

```bash
python -m pip install --upgrade pip
```

## Multiple Terminals with venv

When running both backend and frontend:

**Terminal 1 (Backend):**
```powershell
# Activate venv
.venv\Scripts\Activate.ps1
# Run API
python api_server.py
# Keep running!
```

**Terminal 2 (Frontend):**
```powershell
# No venv needed - this uses Node.js
cd frontend
npm run dev
```

✅ **Important**: Only the backend terminal needs venv active.

## Venv Folder Structure

After creating venv, you'll see:

```
.venv/
├── Scripts/          (Windows) or bin/ (macOS/Linux)
│   ├── Activate.ps1
│   ├── python.exe
│   └── pip.exe
├── Lib/
│   └── site-packages/    (installed packages)
└── pyvenv.cfg
```

**Never edit these files** - they're automatically managed by Python.

## Git and venv

`.venv` is already in `.gitignore`, so it won't be committed to version control.

When cloning the repo on another machine:
1. Create fresh venv: `python -m venv .venv`
2. Activate it: `.venv\Scripts\Activate.ps1`
3. Install deps: `pip install -r requirements.txt`

## Automated Setup

Don't want to manually create venv? Use the automated setup script:

```powershell
.\\setup.ps1
```

This does all the venv setup automatically!

## More Information

- Official venv documentation: https://docs.python.org/3/tutorial/venv.html
- Python download: https://www.python.org/downloads/
- Pip documentation: https://pip.pypa.io/

---

**Summary**: Always activate venv before working with Python packages!

✅ `(.venv)` in prompt = Ready to go  
❌ No `(.venv)` = Activate first with `.venv\Scripts\Activate.ps1`
