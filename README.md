# Haruka Tunnel

Expose your private server to the public internet via SSH tunneling (Reverse Port Forwarding).

## Overview

Haruka Tunnel allows you to:

- Expose private services to the public via SSH tunneling
- Access remote services locally through encrypted tunnels
- Manage multiple ports simultaneously with a single SSH connection
- Store configurations in a local DuckDB database

## Requirements

- Python 3.11+
- SSH Server with public IP and `GatewayPorts yes` enabled
- Private server needing public access
- SSH key-based authentication (RSA)

## Quick Start

### 1. Setup

```bash
git clone https://github.com/faizal2007/haruka-tunnel.git
cd haruka-tunnel
cp env.example .env
```

### 2. Configure .env

```env
SSH_HOST=your.public.server.com
SSH_PORT=22
SSH_USER=root
PRIVATE_KEY_PATH=~/.ssh/id_rsa
FORWARD_HOST=localhost
```

### 3. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Enable Gateway Ports on SSH Server

```bash
# On your SSH server, edit /etc/ssh/sshd_config
GatewayPorts yes

# Restart SSH
systemctl restart sshd
```

## Usage

### PyManage - Interactive CLI Tool

Manage port configurations with an interactive menu:

```bash
./pymanage.py
```

**Menu Options:**

| Option | Description |
|--------|-------------|
| `[1]` | **Create port configuration** - Add new port forwarding rules (unlimited configs in one session) |
| `[2]` | **List all configurations** - View all configs in table format |
| `[3]` | **Start tunnel** - Select and start a specific tunnel with health checks |
| `[4]` | **Update configuration** - Edit existing config fields (name, ports, public IP, description) |
| `[5]` | **Delete configuration** - Remove port configuration |
| `[6]` | **Check port health** - Detect zombie port bindings on SSH server |
| `[7]` | **Kill zombie port** - Force cleanup stale port bindings |
| `[8]` | **Test SSH connection** - Verify SSH connectivity |
| `[0]` | **Exit** - Exit the program |

**Configuration Fields:**

When creating or updating configurations, you'll manage:

1. **Name** - Unique identifier for the configuration (e.g., `web_server`, `flask http`)
2. **Local Port** - Port where your service runs locally (e.g., `5000`)
3. **Bind Port** - Public port on SSH server (e.g., `5000`)
4. **Public IP** - SSH server address or custom IP (defaults to SSH_HOST from `.env`)
5. **Description** - Optional notes about the configuration

**Example Workflow:**

```bash
$ ./pymanage.py

🔧 PYMANAGE - PORT FORWARDING MANAGER 🔧
============================================================

Options:
  [1] Create port configuration
  [2] List all configurations
  [3] Start tunnel
  ...

Choose an option: 1

CREATE PORT CONFIGURATIONS
============================================================
(Type 'cancel' at any prompt to return to main menu)

--- Configuration #1 ---
Configuration name: web_server
Local port: 5000
Bind port: 5000
Public IP (default: bunker.geekdo.me): 
Description: Flask web application
```

**Cancel/Exit During Creation:**

- Type `cancel` at any prompt to return to main menu without completing the config
- After creating a config, choose `[1]` to create another or `[0]` to return to menu

### PyTunnel - Automated Port Forwarding

Start all configured tunnels automatically from the database:

```bash
./pytunnel.py
```

**Features:**

- Reads all port configurations from DuckDB database
- Displays all tunnels with their mappings before starting
- Tests SSH connection to ensure connectivity
- Establishes **single SSH connection** for all tunnels (efficient)
- Starts all tunnels in background for continuous operation
- Graceful shutdown on Ctrl+C
- Supports custom public IPs per configuration

**How It Works:**

1. Loads all configurations from `port_forwarding.db`
2. Tests SSH connection using `.env` credentials
3. Connects to SSH server once
4. Requests port bindings for all configured ports
5. Keeps connection alive and listens for incoming connections
6. Forwards incoming connections to local services

**Configuration Support:**

Each tunnel is configured with:

- **Local Port** - Where your service runs locally
- **Bind Port** - Public port on SSH server
- **Public IP** - Display reference (for user information)
- **Name** - Configuration identifier

**Output Example:**

```text
📋 Found 2 port configuration(s) to forward:

  • web_server: 5000 → bunker.geekdo.me:5000
  • ssh_access: 22 → 107.175.2.25:22025

Connecting to SSH server root@bunker.geekdo.me:22022...
Setting up 2 reverse port forwarding tunnels:
  1. localhost:5000 -> bunker.geekdo.me:5000
  2. localhost:22 -> 107.175.2.25:22025

✓ [web_server] Tunnel active: localhost:5000 → bunker.geekdo.me:5000
✓ [ssh_access] Tunnel active: localhost:22 → 107.175.2.25:22025

✓ Your private services are now publicly accessible
```

**Workflow Example:**

```bash
# 1. Create port configurations using PyManage
./pymanage.py
# [1] Create port configuration (add multiple configs)
# [0] Exit

# 2. Start all tunnels with PyTunnel
./pytunnel.py
# Automatically starts all configured tunnels
# Keep running (Ctrl+C to stop)

# 3. Access your services publicly
# From anywhere: ssh user@bunker.geekdo.me -p 22025
```

**Stopping Tunnels:**

Press `Ctrl+C` to gracefully stop all tunnels:

```bash
^C
Shutting down...
```

### Haruka Class (Programmatic)

Import and use the Haruka class directly in Python:

```python
from __init__ import Haruka

haruka = Haruka()
```

### Reverse Port Forwarding (Expose Private Service)

Expose your private server to the public internet:

```python
# Single port
haruka.reverse_forward_tunnel(
    local_port=5000,      # Your service's port
    bind_port=5000,       # Public port on SSH server
    background=True       # Run in background
)

# Multiple ports simultaneously
port_mappings = [
    (5000, 5000),         # Web service
    (3000, 8080),         # API service
    (8000, 9000),         # WebSocket service
]
haruka.reverse_forward_multiple(port_mappings, background=True)
```

### Local Port Forwarding (Access Remote Services)

Access remote services locally through SSH tunnel:

```python
haruka.forward_local_port(
    local_port=8080,
    remote_host="internal-service.local",
    remote_port=80,
    background=True
)
# Now access at http://localhost:8080
```

### Port Configuration Database

Store and manage port forwarding configurations:

```python
# Initialize database
haruka.init_port_forwarding_db()

# Add configuration
haruka.add_port_config(
    name="web_server",
    local_port=8080,
    remote_host="example.com",
    remote_port=80,
    server_bind_port=8443,
    description="Web server access"
)

# List all configurations
configs = haruka.list_port_configs()

# Get specific configuration
config = haruka.get_port_config("web_server")

# Delete configuration
haruka.delete_port_config("web_server")
```

## Haruka Class Methods

### Core Methods

| Method | Description |
|--------|-------------|
| `test_ssh_connection()` | Verify SSH connection using .env credentials |
| `test_duckdb()` | Test DuckDB database functionality |
| `reverse_forward_tunnel(local_port, bind_port, background)` | Expose single private service publicly |
| `reverse_forward_multiple(port_mappings, background)` | Expose multiple services simultaneously |
| `forward_local_port(local_port, remote_host, remote_port, background)` | Access remote service locally |

### Database Methods

| Method | Description |
|--------|-------------|
| `init_port_forwarding_db()` | Initialize DuckDB database for configurations |
| `add_port_config()` | Add port configuration |
| `list_port_configs()` | List all stored configurations |
| `get_port_config()` | Retrieve specific configuration |
| `delete_port_config()` | Delete configuration |

## Examples

The `examples/` folder contains ready-to-run scripts:

### Reverse Port Forwarding Example

```bash
python examples/reverse_forward_example.py
```

Demonstrates single and multiple port forwarding with interactive menu.

### Multiple Ports Example

```bash
python examples/multiple_ports_example.py
```

Shows how to expose 3 microservices simultaneously.

### Local Port Forwarding Example

```bash
python examples/local_forward_example.py
```

Demonstrates accessing remote services locally.

### Port Database Example

```bash
python examples/port_db_example.py
```

Shows database CRUD operations for managing configurations.

### SSH Connection Test

```bash
python examples/test_ssh.py
```

Verifies SSH connection with credentials from `.env`.

### DuckDB Test

```bash
python examples/test_duckdb.py
```

Tests database functionality.

## Architecture

### Reverse Port Forwarding Flow

```bash
Your Private Server (localhost:5000)
           ↓
    SSH Tunnel (Encrypted)
           ↓
Public SSH Server (bunker.example.com:5000)
           ↓
Public Internet Users
```

### Local Port Forwarding Flow

```bash
Your Computer (localhost:8080)
           ↓
    SSH Tunnel (Encrypted)
           ↓
Remote Service (internal-service.local:80)
```

## Technologies

- Python 3.14 - Latest Python version
- Paramiko 4.0.0 - SSH protocol implementation
- Cryptography 46.0.3 - Encryption utilities
- DuckDB - Embedded SQL database
- python-dotenv 1.0.0 - Environment configuration

## Database Schema

```sql
CREATE TABLE port_configs (
    name VARCHAR NOT NULL UNIQUE,
    local_port INTEGER NOT NULL,
    remote_host VARCHAR NOT NULL,
    remote_port INTEGER NOT NULL,
    server_bind_port INTEGER,
    description VARCHAR,
    active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Common Use Cases

### 1. Expose Web Service

```python
# Web service on localhost:8000 → public at server:8000
haruka.reverse_forward_tunnel(8000, 8000, background=True)
```

### 2. Expose Multiple Microservices

```python
mappings = [
    (5000, 5000),    # Frontend
    (3000, 3000),    # Backend API
    (5432, 5432),    # Database proxy
]
haruka.reverse_forward_multiple(mappings, background=True)
```

### 3. Remote Database Access

```python
# Access remote database locally
haruka.forward_local_port(5432, "db.internal", 5432, background=True)
# Connect to: localhost:5432
```

### 4. SSH Access to Private Server

```python
# Expose private SSH
haruka.reverse_forward_tunnel(22, 22025, background=True)
# SSH via: ssh user@public_server -p 22025
```

## Troubleshooting

### Connection Refused

- Check `.env` configuration
- Verify SSH server has `GatewayPorts yes`
- Ensure private key has correct permissions: `chmod 600 ~/.ssh/id_rsa`

### Authentication Failed

- Verify SSH credentials in `.env`
- Check if public key is in `~/.ssh/authorized_keys` on SSH server
- Regenerate SSH key pair if needed

### Database Errors

- Delete `port_forwarding.db` and reinitialize: `haruka.init_port_forwarding_db()`
- Check write permissions in project directory

## Project Structure

```bash
haruka-tunnel/
├── __init__.py                 # Haruka class implementation
├── pymanage.py                 # Interactive CLI port manager
├── pytunnel.py                 # Automated tunnel startup from DB configs
├── haruka_test.py              # Original HarukaTest class (backup)
├── examples/                    # Example scripts
│   ├── reverse_forward_example.py
│   ├── multiple_ports_example.py
│   ├── local_forward_example.py
│   ├── port_db_example.py
│   ├── test_ssh.py
│   └── test_duckdb.py
├── .env                        # Configuration (create from env.example)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── LICENSE                     # MIT License
```

## Installation from Source

```bash
# Clone repository
git clone https://github.com/faizal2007/haruka-tunnel.git
cd haruka-tunnel

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp env.example .env
# Edit .env with your SSH server details
```

## License

MIT License - See LICENSE file for details

## Author

Faizal Sadri (faizal2007)

## Support

For issues, questions, or contributions:

- Check examples/ folder for usage patterns
- Review test files for functionality verification
- Ensure SSH server has `GatewayPorts yes` enabled
- Verify `.env` configuration is correct
