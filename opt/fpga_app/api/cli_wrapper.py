import subprocess


def program_fpga(port, bitfile):
    cmd = [
        "vivado_lab",
        "-mode",
        "batch",
        "-source",
        "program_fpga.tcl",
        f"PORT={port}",
        f"BIT={bitfile}",
    ]
    subprocess.run(cmd, check=True)
