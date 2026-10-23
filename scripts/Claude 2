#!/bin/bash
# Mnemos Installation Script untuk Termux/LynOS
# Usage: bash setup.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Mnemos - Living Knowledge Network Setup           ║"
echo "║                                                            ║"
echo "║        Memory is not just storage, it's a living network ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment (optional)
echo "[2/5] Setting up environment..."
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "  ✓ Virtual environment created"
else
    source venv/bin/activate
    echo "  ✓ Using existing virtual environment"
fi
echo ""

# Install dependencies
echo "[3/5] Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Create database
echo "[4/5] Initializing database..."
python3 << 'EOF'
from mnemos_db import MnemosDatabase
db = MnemosDatabase()
print("✓ Database initialized")
EOF
echo ""

# Make scripts executable
echo "[5/5] Setting up executable scripts..."
chmod +x mnemos.py
chmod +x example_usage.py

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Installation Complete! ✓                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "Quick Start Commands:"
echo ""
echo "  Start Dashboard:"
echo "    python3 mnemos.py dashboard"
echo "    (or just: python3 mnemos.py)"
echo ""
echo "  Add a Memory:"
echo "    python3 mnemos.py add \"My First Note\""
echo ""
echo "  View All Memories:"
echo "    python3 mnemos.py list"
echo ""
echo "  Search:"
echo "    python3 mnemos.py search \"keyword\""
echo ""
echo "  Load Demo Data:"
echo "    python3 mnemos.py init-demo"
echo ""
echo "  Run Examples:"
echo "    python3 example_usage.py"
echo ""
echo "  Show Help:"
echo "    python3 mnemos.py help"
echo ""
echo "Documentation: Open README.md for full documentation"
echo ""
