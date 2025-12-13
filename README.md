# fpga-server

Simple web UI setup for controlling FPGA boards over the network through USB.

## Introduction

> It is a MUST to use some kind of safety measures to protect the
> server from unauthorized access.
> Risks that may follow by using this server public are not considered.

`fpga-server` is a mini server configuration designed to control FPGA boards
via USB.
It provides a web interface and an API to manage FPGA programming, job queues,
and user authentication.

The server is only tested on Fedora 41/42 Server. Other OS/distros were not
tested.

## Installation

To set up `fpga-server`, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-repo/fpga-server.git
   cd fpga-server
   ```

2. **Download Vivado Lab Edition installation file from [here](https://www.xilinx.com/support/download.html)**

   > You might need AMD account to download the file.

   Place the file in the same directory - inside `fpga-server`.

3. **Run the script:**

   ```bash
   sudo ./init.sh
   ```

   Running the script will install system dependencies, install python dependencies,
   set up virtual environment, initialize the database, create symlinks,
   and configure Supervisor(optional).

   If you need to run part of the scripts manually, use other scripts provided.

> Please understand that we internally moved to use Cloudflare Zero Trust;
> Tailscale may not work as expected.

```bash
# Install system dependencies
./install-dnf-deps.sh
# Install Vivado Lab Edition
./install-vivado-deps.sh
# Install Python dependencies
./install-pip-deps.sh
# Initialize the database
./opt/fpga_app/scripts/init_db.sh
# Create symlinks
./create-symlink.sh
# Configure Supervisor
sudo cp supervisord.conf /etc/supervisord.d/fpga-server.conf
sudo systemctl enable supervisord
sudo systemctl start supervisord
# Set up Tailscale
./setup-tailscale.sh
```

## Usage

### Starting the server

It is highly recommended to use `supervisord` to start up the server,
but you can still manually start it:

```bash
source opt/fpga_app/venv/bin/activate
python opt/fpga_app/api/app.py
```

### Accessing the Web UI

Once the server is running, you can access the web interface in your browser,
at `http://localhost:8000` (or the configured port).

### API Endpoints

The API provides endpoints for:

- User authentication (`/api/auth`)
- FPGA programming (`/api/fpga`)
- Job management (`/api/jobs`)

Refer to `opt/fpga_app/api/README.md` for more details on API usage.

### Creating User

Registering using the web UI is not supported.
The recommended way of creating user is using the python script:

```bash
python3 /opt/fpga_app/scripts/create_user.py
```

Or, you can insert into the user DB yourself, in `/opt/fpga_app/config/jobs.db`.

### Managing Bit Files

`.bit` files uploaded by the users are stored in `/opt/fpga_app/config/bitfiles`.
