#!/bin/sh

set -e

TARGET_DIR="/home/${SUDO_USER:-$USER}/fpga-server/opt/fpga_app/config"

mkdir -p "$TARGET_DIR"

RUNTIME_URL="https://digilent.s3.us-west-2.amazonaws.com/Software/Adept2+Runtime/2.27.9/digilent.adept.runtime-2.27.9.x86_64.rpm"
UTILITIES_URL="https://digilent.s3-us-west-2.amazonaws.com/Software/AdeptUtilities/2.7.1/digilent.adept.utilities-2.7.1.x86_64.rpm"

RUNTIME_FILE="digilent.adept.runtime-2.27.9.x86_64.rpm"
UTILITIES_FILE="digilent.adept.utilities-2.7.1.x86_64.rpm"

echo "Downloading Digilent Adept Runtime to $TARGET_DIR..."
curl -L -o "$TARGET_DIR/$RUNTIME_FILE" "$RUNTIME_URL"

echo "Downloading Digilent Adept Utilities to $TARGET_DIR..."
curl -L -o "$TARGET_DIR/$UTILITIES_FILE" "$UTILITIES_URL"

echo "Downloads complete: $TARGET_DIR"

echo "Installing Digilent Adept Runtime and Utilities..."

dnf install -y \
  "$TARGET_DIR/$RUNTIME_FILE" \
  "$TARGET_DIR/$UTILITIES_FILE"

echo "Testing djtgcfg --version..."

djtgcfg --version

echo "Installing Digilent Adept completed."
