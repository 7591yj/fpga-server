#!/usr/bin/env bash
set -eo pipefail

VIVADO_TAR=$(find . -maxdepth 1 -type f -name '*Vivado*' | head -n1 || true)

if [[ -n "$VIVADO_TAR" ]]; then
  echo "Vivado TAR path: $VIVADO_TAR"
  echo "found Vivado install tar, starting installation..."
else
  echo "Vivado installation was not found. Aborting installation."
  exit 1
fi

if compgen -G "/tools/Xilinx/Vivado_Lab/*" >/dev/null; then
  echo "Vivado installation already exists. Skipping Vivado installation."
else
  echo "extracting Vivado installation..."
  tar -xvf "$VIVADO_TAR" -C /opt

  echo "running batch installation..."
  VIVADO_DIR="${VIVADO_TAR#./}"
  VIVADO_DIR="${VIVADO_DIR%.tar}"
  cd "/opt/$VIVADO_DIR"
  sudo ./xsetup --batch Install --agree XilinxEULA,3rdPartyEULA --edition "Vivado Lab Edition (Standalone)" --location /tools/Xilinx/Vivado_Lab
fi

echo "installing cable drivers..."
VIVADO_VER=$(echo "Vivado_Lab_Lin_2025.2_1114_2157" | grep -oE '[0-9]{4}\.[0-9]+')
cd "/tools/Xilinx/Vivado_Lab/${VIVADO_VER}/data/xicom/cable_drivers/lin64/install_script/install_drivers/"
sudo ./install_drivers

grep -qxF "source /tools/Xilinx/Vivado_Lab/${VIVADO_VER}/Vivado_Lab/settings64.sh" /home/"${SUDO_USER:-$USER}"/.bashrc ||
  echo "source /tools/Xilinx/Vivado_Lab/${VIVADO_VER}/Vivado_Lab/settings64.sh" >>/home/"${SUDO_USER:-$USER}"/.bashrc

# shellcheck disable=SC1090
source "/home/${SUDO_USER:-$USER}/.bashrc"

echo "Installing Vivado Lab Edition completed."
