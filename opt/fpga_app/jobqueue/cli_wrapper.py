import subprocess


def program_fpga(serial, bitfile):
    cmd = [
        "vivado_lab",
        "-mode",
        "batch",
        "-source",
        "/opt/fpga_app/scripts/program_fpga.tcl",
        f'-tclargs "{bitfile}" "{serial}"',
    ]
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def find_devices():
    cmd = [
        "vivado_lab",
        "-mode",
        "batch",
        "-source",
        "/opt/fpga_app/queue/find_devices.tcl",
    ]

    result = subprocess.run(cmd, check=True, capture_output=True, text=True)

    lines = []
    for raw in result.stdout.splitlines():
        line = raw.strip()
        # reject Vivado command echoes, comments, and info lines
        if (
            not line
            or line.startswith("INFO:")
            or line.startswith("#")
            or line.startswith("puts")
            or line.startswith("open_hw")
            or line.startswith("connect_hw")
            or line.startswith("foreach")
        ):
            continue
        if "|" not in line:
            continue
        lines.append(line)

    devices = []
    for line in lines:
        parts = line.split("|")
        if len(parts) != 5:
            continue
        devices.append(
            dict(
                device_name=parts[0],
                device_id=parts[1],
                transport_type=parts[2],
                product_name=parts[3],
                serial_number=parts[4],
            )
        )
    return devices
