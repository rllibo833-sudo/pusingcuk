# Mnemos Installation Guide

Installation guide untuk berbagai platform, dengan fokus khusus pada Termux dan LynOS.

## 📋 Requirements

### Minimum Requirements
- Python 3.8+
- pip (Python package manager)
- ~50MB disk space

### Supported Platforms
- ✅ Termux (Android)
- ✅ LynOS (Debian-based)
- ✅ macOS
- ✅ Windows (PowerShell/CMD)
- ✅ Linux (Ubuntu, Fedora, etc)

---

## 🚀 Quick Install (All Platforms)

### Step 1: Get the Files
```bash
# Download atau clone
# Pastikan semua file .py ada di satu folder
cd mnemos
```

### Step 2: Install Python (jika belum ada)

**Termux:**
```bash
pkg install python
```

**macOS:**
```bash
brew install python3
```

**Ubuntu/Debian:**
```bash
sudo apt-get install python3 python3-pip
```

**Windows:**
Download dari https://python.org atau gunakan:
```powershell
winget install Python.Python.3.11
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

atau:
```bash
pip install rich==13.7.0 psutil==5.9.6
```

### Step 4: Run
```bash
# Interactive dashboard
python3 mnemos.py

# atau
python3 mnemos.py dashboard
```

---

## 🔧 Detailed Platform Setup

### Termux Setup (Android)

#### Prerequisites
```bash
# Update package manager
pkg update
pkg upgrade

# Install Python
pkg install python

# Install git (optional, untuk clone)
pkg install git
```

#### Installation
```bash
# Navigate to home
cd ~

# Create directory
mkdir mnemos
cd mnemos

# Copy all .py files here
# (atau gunakan git clone jika available)

# Install dependencies
pip install -r requirements.txt

# Make executable
chmod +x mnemos.py
chmod +x setup.sh
```

#### Running
```bash
# Quick start
python3 mnemos.py

# Atau dengan specific command
python3 mnemos.py dashboard
python3 mnemos.py add "Test Note"
python3 mnemos.py list
```

#### Keep Running in Background
```bash
# Using nohup
nohup python3 mnemos.py dashboard > mnemos.log 2>&1 &

# Or use tmux
pkg install tmux
tmux new-session -d -s mnemos 'python3 mnemos.py dashboard'

# View session
tmux attach-session -t mnemos
```

### LynOS / Linux Setup

#### Prerequisites
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# Fedora/RedHat
sudo dnf install python3 python3-pip

# Arch
sudo pacman -S python python-pip
```

#### Installation
```bash
# Navigate to project directory
mkdir -p ~/projects/mnemos
cd ~/projects/mnemos

# Copy files

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make executable
chmod +x mnemos.py
chmod +x setup.sh
```

#### Automated Setup
```bash
# Run setup script
bash setup.sh
```

#### Running as Service (Optional)
Create `/etc/systemd/system/mnemos.service`:
```ini
[Unit]
Description=Mnemos Living Knowledge Network
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/home/yourusername/projects/mnemos
ExecStart=/usr/bin/python3 /home/yourusername/projects/mnemos/mnemos.py dashboard
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable dan start:
```bash
sudo systemctl enable mnemos
sudo systemctl start mnemos
sudo systemctl status mnemos
```

### macOS Setup

#### Using Homebrew
```bash
# Install Python (if not installed)
brew install python3

# Navigate to project
mkdir -p ~/Developer/mnemos
cd ~/Developer/mnemos

# Copy files

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make executable
chmod +x mnemos.py
```

#### Running
```bash
# Simple
python3 mnemos.py

# Or with background process
nohup python3 mnemos.py dashboard > mnemos.log 2>&1 &
```

### Windows Setup

#### Using PowerShell
```powershell
# Navigate to directory
cd C:\Users\YourName\Documents
mkdir mnemos
cd mnemos

# Copy all .py files here

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

#### Running
```powershell
# Run
python mnemos.py

# Or specific command
python mnemos.py dashboard
python mnemos.py add "Test"
```

---

## ✅ Verification

Setelah installation, verify bahwa semuanya berjalan:

```bash
# Check Python version
python3 --version

# Check dependencies installed
python3 -c "import rich; import psutil; print('✓ All dependencies OK')"

# Test Mnemos
python3 mnemos.py init-demo

# Check database created
ls -la mnemos.db
```

---

## 🐛 Troubleshooting

### Error: "No module named 'rich'"

**Solution:**
```bash
pip install rich
# atau
pip install --upgrade rich
```

### Error: "ModuleNotFoundError: No module named 'psutil'"

**Solution:**
```bash
pip install psutil
```

### Error: "Permission denied: mnemos.py"

**Solution:**
```bash
chmod +x mnemos.py
python3 mnemos.py  # Run with python3 directly
```

### Database Lock Error

**Solution:**
```bash
# Check running processes
ps aux | grep mnemos

# Kill if hanging
kill -9 <PID>

# Remove lock file if exists
rm mnemos.db-journal

# Try again
python3 mnemos.py
```

### Import Error with SQLite

**Solution:**
```bash
# Sometimes SQLite needs to be installed
# Termux
pkg install sqlite

# Ubuntu
sudo apt-get install sqlite3 libsqlite3-dev

# macOS
brew install sqlite
```

### Terminal Display Issues

**Solution:**
Make sure terminal supports Unicode:
```bash
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Then run mnemos
python3 mnemos.py
```

---

## 📦 Alternative: Docker Setup (Optional)

Jika menggunakan Docker:

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /mnemos

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "mnemos.py"]
CMD ["dashboard"]
```

**Build & Run:**
```bash
docker build -t mnemos .
docker run -it mnemos
```

---

## 🔄 Updating Mnemos

```bash
# Download latest files
# Copy over existing files (backup first!)

# Update dependencies
pip install --upgrade -r requirements.txt

# Restart
python3 mnemos.py
```

---

## 💾 Database Location

Default locations:

- **Termux**: `~/mnemos/mnemos.db`
- **Linux**: `~/projects/mnemos/mnemos.db`
- **macOS**: `~/Developer/mnemos/mnemos.db`
- **Windows**: `C:\Users\YourName\Documents\mnemos\mnemos.db`

Untuk mengubah lokasi, edit di `mnemos.py`:
```python
ui = MnemosUI()
# Change database path in MnemosDatabase("custom_path.db")
```

---

## 🎯 Next Steps

1. **Start Dashboard:**
   ```bash
   python3 mnemos.py
   ```

2. **Load Demo Data:**
   ```bash
   python3 mnemos.py init-demo
   ```

3. **Read Documentation:**
   See `README.md` untuk lengkap commands dan features

4. **Run Examples:**
   ```bash
   python3 example_usage.py
   ```

---

## 📞 Support

Jika mengalami masalah:

1. Check semua requirements sudah installed
2. Verify Python version (3.8+)
3. Check internet connection (jika cloud sync)
4. See README.md FAQ section
5. Check terminal/shell compatibility

---

## ✨ You're All Set!

Mnemos is ready to use. Start creating memories and building your knowledge network!

```
 ▶ Mnemos
   Living Knowledge Network
   Memory is not just storage, it's a living network.
```

Happy memory building! 🧠💜
