#!/usr/bin/env bash
set -euo pipefail

dnf update -y

dnf install -y \
  git \
  ansible \
  python3-pip \
  tailscale \
  sqlite \
  jq \
  usbutils \
  avahi-libs

if systemctl list-unit-files | grep -q '^firewalld\.service'; then
  sudo systemctl disable firewalld --now
  echo "firewalld disabled."
else
  echo "firewalld not found; skipping disable step."
fi

echo "Installing dnf deps completed."
