#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   export AUTH_KEY="tskey-abc123..."
#   sudo ./tailscale-setup.sh
#
# or
#   sudo AUTH_KEY="tskey-abc123..." ./tailscale-setup.sh

if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root or with sudo."
  exit 1
fi

if [[ -z "${AUTH_KEY:-}" ]]; then
  echo "Error: AUTH_KEY environment variable not set."
  exit 1
fi

tailscale up --authkey "$AUTH_KEY" --hostname fpga-server --ssh

echo "Tailscale setup complete."
