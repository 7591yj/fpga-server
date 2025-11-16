#!/usr/bin/env bash
set -euo pipefail

run_script() {
  echo "Running $1..."
  if sudo ./"$1"; then
    echo "$1 completed successfully."
  else
    echo "Error running $1. Aborting."
    exit 1
  fi
  echo
}

run_script_user() {
  echo "Running $1 as user..."
  if ./"$1"; then
    echo "$1 completed successfully."
  else
    echo "Error running $1. Aborting."
    exit 1
  fi
  echo
}

run_script_path() {
  echo "Running $1..."
  if sudo "$1"; then
    echo "$1 completed successfully."
  else
    echo "Error running $1. Aborting."
    exit 1
  fi
  echo
}

# check if running as root
if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root or with sudo."
  exit 1
fi

# run installation scripts
run_script "install-dnf-deps.sh"
run_script "install-adept.sh"
run_script_user "install-pip-deps.sh"
run_script_user "create-symlink.sh"
run_script_path "opt/fpga_app/scripts/init_db.sh"

# ask about supervisord
read -p "Do you want to set up and start supervisord? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "Setting up supervisord..."
  mkdir -p /etc/supervisord.d
  cp supervisord.conf /etc/supervisord.d/fpga-server.ini
  systemctl enable supervisord
  systemctl start supervisord
  echo "supervisord setup complete."
fi

# ask about Tailscale
read -p "Do you want to set up and start Tailscale? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "Please enter your Tailscale AUTH_KEY:"
  read -r AUTH_KEY
  export AUTH_KEY
  echo "Running Tailscale setup..."
  if sudo ./setup-tailscale.sh; then
    echo "Tailscale setup script completed."
  else
    echo "Tailscale setup script failed."
  fi
fi

echo "Initialization complete."
