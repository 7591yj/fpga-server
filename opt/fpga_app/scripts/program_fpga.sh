#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <bitfile> <device_sn>" >&2
  exit 1
fi
BITFILE="$1"
DEVICE_SN="$2"

if [[ ! -f "$BITFILE" ]]; then
  echo "bitstream not found: $BITFILE" >&2
  exit 1
fi

source /tools/Xilinx/Vivado_Lab/2025.2/Vivado_Lab/settings64.sh
vivado_lab -mode batch -source /opt/fpga_app/scripts/program_fpga.tcl -tclargs "$BITFILE" "$DEVICE_SN"
echo "Programmed FPGA with $BITFILE"
