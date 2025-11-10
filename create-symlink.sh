#!/usr/bin/env bash
set -euo pipefail

# Move symlinks for fpga_app from ~/fpga-server/ into proper system positions

SRC_BASE="/home/${SUDO_USER:-$USER}/fpga-server"

# Expected mapping: local project dir → system target
declare -A TARGETS=(
  ["$SRC_BASE/opt/fpga_app/api"]="/opt/fpga_app/api"
  ["$SRC_BASE/opt/fpga_app/config"]="/opt/fpga_app/config"
  ["$SRC_BASE/opt/fpga_app/queue"]="/opt/fpga_app/queue"
  ["$SRC_BASE/opt/fpga_app/scripts"]="/opt/fpga_app/scripts"
  ["$SRC_BASE/opt/fpga_app/webui"]="/opt/fpga_app/webui"
  ["$SRC_BASE/var/log/fpga_app"]="/var/log/fpga_app"
  ["$SRC_BASE/mnt/backup"]="/mnt/backup"
)

echo "Creating target directories and symlinks from $SRC_BASE..."

for SRC in "${!TARGETS[@]}"; do
  DST="${TARGETS[$SRC]}"

  # Ensure source exists
  if [[ ! -d "$SRC" ]]; then
    echo "Creating missing source directory: $SRC"
    sudo -u "${SUDO_USER:-$USER}" mkdir -p "$SRC"
  fi

  # Create parent directory for target
  mkdir -p "$(dirname "$DST")"

  # Remove existing symlink or directory if necessary
  if [[ -L "$DST" || -d "$DST" ]]; then
    rm -rf "$DST"
  fi

  ln -s "$SRC" "$DST"
  echo "Linked $DST -> $SRC"
done

echo "Creating symlinks completed."
