#!/bin/bash
# Quick launch script for the spaceship game

echo "🚀 Spaceship Animation - Enhanced Edition"
echo "=========================================="
echo ""

# Check if pygame is installed
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "⚠️  Pygame not installed. Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

echo "✓ Starting game..."
echo "  Controls: Arrow/WASD=Move, Space=Fire, 1-4=Weapons, Esc=Quit"
echo ""

python3 main.py
