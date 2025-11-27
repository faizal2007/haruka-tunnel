# PyManage - Port Forwarding Manager

Interactive CLI tool for managing port forwarding configurations using Haruka.

## Features

✨ **Main Features:**
- 🎛️ Interactive panel interface
- 📝 Create port configurations
- 📋 List all configurations
- 👁️ View configuration details
- ✏️ Update existing configurations
- 🗑️ Delete configurations
- 🔍 Check port health on SSH server
- ⚡ Kill zombie port bindings
- 🧪 Test SSH connection
- 🤖 Auto-initialize database on startup

## Usage

### Interactive Mode
```bash
# Run the interactive panel
./pymanage.py

# Or
python3 pymanage.py
```

### Menu Options
```
1 - Create port configuration
2 - List all configurations
3 - View configuration details
4 - Update configuration
5 - Delete configuration
6 - Check port health
7 - Kill zombie port
8 - Test SSH connection
0 - Exit
```

## Example Workflows

### Create a New Port Configuration
```
Option: 1
Configuration name: webserver
Local port: 3000
Bind port: 5000
Remote host: localhost
Remote port: 3000
Description: My web application
```

This creates a configuration to expose localhost:3000 to the public as port 5000 on your SSH server.

### Monitor Port Health
```
Option: 6
Enter bind port to check: 5000
```

This checks if port 5000 on the SSH server is actively listening or has a zombie binding.

### Clean Up Zombie Ports
```
Option: 7
Enter bind port to kill: 5000
```

This forcefully kills the process holding the port and frees it for reuse.

### Batch Management
Use the Python API directly:

```python
from pymanage import PyManage

manager = PyManage()
haruka = manager.haruka

# Create multiple configurations
haruka.add_port_config("api", 8000, "localhost", 8000, 5000, "API Server")
haruka.add_port_config("web", 3000, "localhost", 3000, 5001, "Web App")

# List all
configs = haruka.list_port_configs()
for config in configs:
    print(f"{config['name']}: {config['local_port']} -> {config['server_bind_port']}")

# Get specific config
api = haruka.get_port_config("api")

# Delete config
haruka.delete_port_config("web")

# Check port health
health = haruka.check_port_health_ssh_server(5000)
if health['status'] == 'zombie':
    haruka.kill_zombie_port_ssh_server(5000)
```

## Database

PyManage automatically initializes a DuckDB database (`port_forwarding.db`) on first run.

The database stores:
- Configuration name (unique)
- Local port
- Remote host and port
- Server bind port
- Description
- Active status
- Timestamps

## Examples

Run the example script to see PyManage in action:

```bash
python3 examples/pymanage_examples.py
```

This demonstrates:
1. Basic CRUD operations
2. Port health monitoring
3. Auto-cleanup before tunnel
4. Batch operations
5. Testing connections

## Key Functions Used

PyManage uses all available functions from Haruka:

**Configuration Management:**
- `add_port_config()` - Create configuration
- `list_port_configs()` - List all configs
- `get_port_config()` - Get specific config
- `delete_port_config()` - Delete configuration

**Port Management:**
- `check_port_health_ssh_server()` - Check if port is healthy/zombie
- `kill_zombie_port_ssh_server()` - Kill zombie port binding

**Testing:**
- `test_ssh_connection()` - Test SSH access
- `test_duckdb()` - Test database operations
- `init_port_forwarding_db()` - Initialize database

## Requirements

- `.env` file with SSH configuration:
  - `SSH_HOST` - SSH server hostname
  - `SSH_USER` - SSH username
  - `SSH_PORT` - SSH port (default: 22)
  - `PRIVATE_KEY_PATH` - Path to private key
  - `FORWARD_HOST` - Forward host (default: localhost)

## Troubleshooting

### Database Already Exists Error
The database initializes automatically on first run. Delete `port_forwarding.db` to reset it.

### SSH Connection Failed
Check your `.env` file for correct SSH credentials and private key path.

### Zombie Port Won't Kill
The zombie port may be protected by firewall rules. SSH to your server and manually check:
```bash
lsof -i :5000
netstat -tulnp | grep 5000
```

## Tips

1. **Always check port health** before starting new tunnels
2. **Clean up zombie ports** when tunnels break unexpectedly
3. **Use batch operations** for managing multiple services
4. **Monitor regularly** to prevent port conflicts
5. **Keep configurations documented** with descriptions
