#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <bitfile>" >&2
  exit 1
fi

BITFILE="$1"

if [[ ! -f "$BITFILE" ]]; then
  echo "bitstream not found: $BITFILE" >&2
  exit 1
fi

vivado_lab -mode batch -source /opt/fpga_app/scripts/program_fpga.tcl -tclargs "$BITFILE"
echo "Programmed FPGA with $BITFILE"
