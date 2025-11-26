import subprocess


def program_fpga(serial, bitfile):
    cmd = [
        "vivado_lab",
        "-mode",
        "batch",
        "-source",
        "/opt/fpga_app/scripts/program_fpga.tcl",
        f"SERIAL={serial}",
        f"BITFILE={bitfile}",
    ]
    subprocess.run(cmd, check=True)
