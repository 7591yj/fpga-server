#!/bin/bash
set -e

APP_DIR="/home/${SUDO_USER:-$USER}/fpga-server/opt/fpga_app"
VENV_DIR="$APP_DIR/venv"

echo "Removing existing venv..."
rm -rf "$VENV_DIR"

echo "Creating new virtual environment..."
python3 -m venv "$VENV_DIR"

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies..."
pip install -r "$APP_DIR/requirements.txt"

echo "Installing pip deps completed."
