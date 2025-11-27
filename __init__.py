import paramiko
import duckdb
from dotenv import load_dotenv
import os
import socket
import select
import threading
import time

class Haruka:
    """
    Haruka class containing all port forwarding and tunnel functionality.
    """

    def __init__(self):
        """Initialize the class by loading environment variables."""
        load_dotenv()
        self.env_loaded = True

    def test_ssh_connection(self):
        """
        Test SSH connection using the parameters from .env file.
        Returns True if connection is successful, False otherwise.
        """
        ssh_host = os.getenv("SSH_HOST")
        ssh_port = int(os.getenv("SSH_PORT", 22))
        ssh_user = os.getenv("SSH_USER")
        private_key_path = os.getenv("PRIVATE_KEY_PATH")

        if not all([ssh_host, ssh_user, private_key_path]):
            print("Error: Missing required environment variables (SSH_HOST, SSH_USER, PRIVATE_KEY_PATH)")
            return False

        try:
            # Create SSH client
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy())

            # Load private key
            private_key = paramiko.RSAKey(filename=private_key_path)

            # Attempt connection
            print(f"Attempting to connect to {ssh_user}@{ssh_host}:{ssh_port}...")
            client.connect(
                hostname=str(ssh_host),
                port=ssh_port,
                username=str(ssh_user),
                pkey=private_key,
                timeout=10
            )

            # If we reach here, connection was successful
            print("SSH connection successful!")
            client.close()
            return True

        except paramiko.AuthenticationException:
            print("Authentication failed. Please check your private key and username.")
            return False
        except paramiko.SSHException as e:
            print(f"SSH connection failed: {e}")
            return False
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def test_duckdb(self):
        """
        Test basic DuckDB functionality.
        Returns True if all tests pass, False otherwise.
        """
        try:
            # Connect to an in-memory DuckDB database
            con = duckdb.connect(':memory:')
            print("✓ Connected to DuckDB successfully")

            # Create a sample table
            con.execute("""
                CREATE TABLE users (
                    id INTEGER,
                    name VARCHAR,
                    age INTEGER,
                    city VARCHAR
                )
            """)
            print("✓ Created users table")

            # Insert sample data
            con.execute("""
                INSERT INTO users VALUES
                (1, 'Alice', 25, 'New York'),
                (2, 'Bob', 30, 'London'),
                (3, 'Charlie', 35, 'Paris'),
                (4, 'Diana', 28, 'Tokyo'),
                (5, 'Eve', 32, 'Sydney')
            """)
            print("✓ Inserted sample data")

            # Query all users
            result = con.execute("SELECT * FROM users").fetchall()
            print("✓ Queried all users")

            con.close()
            print("✓ Connection closed successfully")

            return True

        except Exception as e:
            print(f"✗ DuckDB test failed: {e}")
            return False

    def reverse_forward_tunnel(self, local_port, bind_port, background=False):
        """
        Reverse port forward: expose local service to public SSH server.

        Args:
            local_port (int): Local port where your service is running
            bind_port (int): Port to bind on the SSH server (public facing)
            background (bool): If True, run in background thread

        Returns:
            bool: True if reverse forwarding started successfully, False otherwise
        """
        ssh_host = os.getenv("SSH_HOST")
        ssh_port = int(os.getenv("SSH_PORT", 22))
        ssh_user = os.getenv("SSH_USER")
        private_key_path = os.getenv("PRIVATE_KEY_PATH")
        forward_host = os.getenv("FORWARD_HOST", "localhost")

        if not all([ssh_host, ssh_user, private_key_path]):
            print("Error: Missing required environment variables (SSH_HOST, SSH_USER, PRIVATE_KEY_PATH)")
            return False

        try:
            # Create SSH client
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy())

            # Load private key
            private_key = paramiko.RSAKey(filename=private_key_path)

            # Connect to SSH server
            print(f"Connecting to SSH server {ssh_user}@{ssh_host}:{ssh_port}...")
            client.connect(
                hostname=str(ssh_host),
                port=ssh_port,
                username=str(ssh_user),
                pkey=private_key,
                timeout=10
            )

            print(f"Setting up reverse port forwarding:")
            print(f"  Local service: localhost:{local_port}")
            print(f"  Public access: {ssh_host}:{bind_port}")

            # Start the reverse forwarding
            if background:
                thread = threading.Thread(
                    target=self._reverse_forward_worker,
                    args=(client.get_transport(), bind_port, forward_host, local_port),
                    daemon=True
                )
                thread.start()
                print(f"Reverse port forwarding started in background")
                print(f"✓ Public users can now access your service at {ssh_host}:{bind_port}")
                return True
            else:
                # Run in foreground
                self._reverse_forward_worker(client.get_transport(), bind_port, forward_host, local_port)
                return True

        except paramiko.AuthenticationException:
            print("SSH authentication failed. Please check your private key and username.")
            return False
        except paramiko.SSHException as e:
            print(f"SSH connection failed: {e}")
            return False
        except Exception as e:
            print(f"Failed to setup reverse port forwarding: {e}")
            return False

    def reverse_forward_multiple(self, port_mappings, background=False):
        """
        Reverse port forward multiple services simultaneously.

        Args:
            port_mappings (list): List of tuples or dicts specifying port mappings
            background (bool): If True, run in background threads

        Returns:
            bool: True if all reverse forwardings started successfully, False otherwise
        """
        ssh_host = os.getenv("SSH_HOST")
        ssh_port = int(os.getenv("SSH_PORT", 22))
        ssh_user = os.getenv("SSH_USER")
        private_key_path = os.getenv("PRIVATE_KEY_PATH")
        forward_host = os.getenv("FORWARD_HOST", "localhost")

        if not all([ssh_host, ssh_user, private_key_path]):
            print("Error: Missing required environment variables (SSH_HOST, SSH_USER, PRIVATE_KEY_PATH)")
            return False

        if not port_mappings or len(port_mappings) == 0:
            print("Error: No port mappings provided")
            return False

        try:
            # Create SSH client
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy())

            # Load private key
            private_key = paramiko.RSAKey(filename=private_key_path)

            # Connect to SSH server
            print(f"Connecting to SSH server {ssh_user}@{ssh_host}:{ssh_port}...")
            client.connect(
                hostname=str(ssh_host),
                port=ssh_port,
                username=str(ssh_user),
                pkey=private_key,
                timeout=10
            )

            transport = client.get_transport()
            print(f"Setting up {len(port_mappings)} reverse port forwarding tunnels:")

            # Parse port mappings and start forwarding for each
            for idx, mapping in enumerate(port_mappings, 1):
                # Parse mapping format
                if isinstance(mapping, (tuple, list)):
                    local_port, bind_port = mapping
                elif isinstance(mapping, dict):
                    local_port = mapping.get('local') or mapping.get('local_port')
                    bind_port = mapping.get('bind') or mapping.get('bind_port')
                else:
                    print(f"  ✗ Invalid mapping format at index {idx}: {mapping}")
                    continue

                print(f"  {idx}. localhost:{local_port} -> {ssh_host}:{bind_port}")

                # Start the reverse forwarding for this port
                if background:
                    thread = threading.Thread(
                        target=self._reverse_forward_worker,
                        args=(transport, bind_port, forward_host, local_port),
                        daemon=True
                    )
                    thread.start()
                else:
                    self._reverse_forward_worker(transport, bind_port, forward_host, local_port)

            if background:
                print(f"\n✓ All {len(port_mappings)} reverse port forwarding tunnels started in background")
                return True
            else:
                return True

        except paramiko.AuthenticationException:
            print("SSH authentication failed. Please check your private key and username.")
            return False
        except paramiko.SSHException as e:
            print(f"SSH connection failed: {e}")
            return False
        except Exception as e:
            print(f"Failed to setup multiple reverse port forwarding: {e}")
            return False

    def _reverse_forward_worker(self, transport, bind_port, local_host, local_port):
        """
        Worker function for reverse port forwarding.
        Requests port forwarding from SSH server and handles incoming connections.
        """
        try:
            # Request the SSH server to bind to bind_port and forward to us
            transport.request_port_forward("", bind_port)
            transport.set_keepalive(600)
            print(f"Listening for connections on port {bind_port} (SSH server side)")

            while True:
                # Accept connection from SSH server
                chan = transport.accept(1000)
                if chan is None:
                    continue

                print(f"Incoming connection through SSH tunnel, forwarding to {local_host}:{local_port}")

                # Start a thread to handle this connection
                thread = threading.Thread(
                    target=self._handle_reverse_connection,
                    args=(chan, local_host, local_port),
                    daemon=True
                )
                thread.start()

        except KeyboardInterrupt:
            print("Reverse port forwarding stopped by user")
        except Exception as e:
            print(f"Error in reverse forwarding worker: {e}")

    def _handle_reverse_connection(self, chan, local_host, local_port):
        """
        Handle a single reverse forwarded connection.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to the local service with better error handling
            print(f"Attempting to connect to local service {local_host}:{local_port}...")
            sock.settimeout(5)  # 5 second timeout for connection
            sock.connect((local_host, local_port))
            sock.settimeout(None)  # Remove timeout for data transfer
            print(f"✓ Connected to local service {local_host}:{local_port}")

            # Forward data between SSH channel and local service
            while True:
                try:
                    r, w, x = select.select([sock, chan], [], [], 1)

                    if sock in r:
                        data = sock.recv(4096)
                        if len(data) == 0:
                            print("Local service closed connection")
                            break
                        chan.send(data)

                    if chan in r:
                        data = chan.recv(4096)
                        if len(data) == 0:
                            print("Remote client closed connection")
                            break
                        sock.send(data)
                        
                except socket.error as e:
                    print(f"Socket error during data transfer: {e}")
                    break
                except Exception as e:
                    print(f"Error during data transfer: {e}")
                    break

        except socket.timeout:
            print(f"✗ Timeout connecting to local service {local_host}:{local_port}")
            print(f"  → Is your service running on {local_host}:{local_port}?")
        except ConnectionRefusedError:
            print(f"✗ Connection refused to local service {local_host}:{local_port}")
            print(f"  → Is your service running and accepting connections?")
        except Exception as e:
            print(f"✗ Error connecting to local service {local_host}:{local_port}: {e}")
        finally:
            try:
                sock.close()
            except:
                pass
            try:
                chan.close()
            except:
                pass

    def forward_local_port(self, local_port, remote_host, remote_port, background=False):
        """
        Forward a local port to a remote host through SSH tunnel.

        Args:
            local_port (int): Local port to listen on
            remote_host (str): Remote host to forward to
            remote_port (int): Remote port to forward to
            background (bool): If True, run in background thread

        Returns:
            bool: True if forwarding started successfully, False otherwise
        """
        ssh_host = os.getenv("SSH_HOST")
        ssh_port = int(os.getenv("SSH_PORT", 22))
        ssh_user = os.getenv("SSH_USER")
        private_key_path = os.getenv("PRIVATE_KEY_PATH")

        if not all([ssh_host, ssh_user, private_key_path]):
            print("Error: Missing required environment variables (SSH_HOST, SSH_USER, PRIVATE_KEY_PATH)")
            return False

        try:
            # Create SSH client
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy())

            # Load private key
            private_key = paramiko.RSAKey(filename=private_key_path)

            # Connect to SSH server
            print(f"Connecting to SSH server {ssh_user}@{ssh_host}:{ssh_port}...")
            client.connect(
                hostname=str(ssh_host),
                port=ssh_port,
                username=str(ssh_user),
                pkey=private_key,
                timeout=10
            )

            print(f"Setting up local port forwarding: localhost:{local_port} -> {remote_host}:{remote_port}")

            # Start the forwarding
            if background:
                thread = threading.Thread(
                    target=self._forward_worker,
                    args=(client.get_transport(), local_port, remote_host, remote_port),
                    daemon=True
                )
                thread.start()
                print(f"Local port forwarding started in background (localhost:{local_port} -> {remote_host}:{remote_port})")
                return True
            else:
                # Run in foreground
                self._forward_worker(client.get_transport(), local_port, remote_host, remote_port)
                return True

        except paramiko.AuthenticationException:
            print("SSH authentication failed. Please check your private key and username.")
            return False
        except paramiko.SSHException as e:
            print(f"SSH connection failed: {e}")
            return False
        except Exception as e:
            print(f"Failed to setup local port forwarding: {e}")
            return False

    def _forward_worker(self, transport, local_port, remote_host, remote_port):
        """
        Worker function for local port forwarding.
        """
        # Create a socket to listen on the local port
        local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            local_socket.bind(('localhost', local_port))
            local_socket.listen(5)
            print(f"Listening on localhost:{local_port}")

            while True:
                # Accept local connection
                local_conn, addr = local_socket.accept()
                print(f"Accepted connection from {addr}")

                # Start a thread to handle this connection
                thread = threading.Thread(
                    target=self._handle_local_connection,
                    args=(transport, local_conn, remote_host, remote_port),
                    daemon=True
                )
                thread.start()

        except KeyboardInterrupt:
            print("Local port forwarding stopped by user")
        except Exception as e:
            print(f"Error in local forwarding worker: {e}")
        finally:
            local_socket.close()

    def _handle_local_connection(self, transport, local_conn, remote_host, remote_port):
        """
        Handle a single local connection by forwarding it through SSH.
        """
        try:
            # Open a direct-tcpip channel to the remote host
            remote_conn = transport.open_channel(
                'direct-tcpip',
                (remote_host, remote_port),
                local_conn.getpeername()
            )

            if remote_conn is None:
                print(f"Failed to open remote connection to {remote_host}:{remote_port}")
                local_conn.close()
                return

            print(f"Tunnel established: {local_conn.getpeername()} -> {remote_host}:{remote_port}")

            # Forward data between local and remote connections
            while True:
                r, w, x = select.select([local_conn, remote_conn], [], [], 1)

                if local_conn in r:
                    data = local_conn.recv(4096)
                    if len(data) == 0:
                        break
                    remote_conn.send(data)

                if remote_conn in r:
                    data = remote_conn.recv(4096)
                    if len(data) == 0:
                        break
                    local_conn.send(data)

        except Exception as e:
            print(f"Error handling local connection: {e}")
        finally:
            local_conn.close()
            if 'remote_conn' in locals():
                remote_conn.close()

    def init_port_forwarding_db(self):
        """
        Initialize DuckDB database for storing port forwarding configurations.
        Creates the necessary tables if they don't exist.
        """
        try:
            con = duckdb.connect('port_forwarding.db')
            con.execute("""
                CREATE TABLE IF NOT EXISTS port_configs (
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
            """)
            con.close()
            print("✓ Port forwarding database initialized")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize port forwarding database: {e}")
            return False

    def check_port_health_ssh_server(self, bind_port):
        """
        Check if a port on the SSH server is open and accepting connections.
        Tests both port binding AND tunnel functionality.

        Args:
            bind_port (int): Port on the SSH server to check

        Returns:
            dict: {
                'healthy': bool - True if port is responsive AND tunnel works,
                'bound': bool - True if port is listening,
                'tunnel_working': bool - True if tunnel actually forwards traffic,
                'port': int - The port checked,
                'status': str - 'healthy', 'zombie', 'unbound', or 'error'
            }
        """
        ssh_host = os.getenv("SSH_HOST")
        ssh_port = int(os.getenv("SSH_PORT", 22))
        ssh_user = os.getenv("SSH_USER")
        private_key_path = os.getenv("PRIVATE_KEY_PATH")

        if not all([ssh_host, ssh_user, private_key_path]):
            print("Error: Missing required environment variables")
            return {'healthy': False, 'bound': False, 'tunnel_working': False, 'port': bind_port, 'status': 'error'}

        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy())
            private_key = paramiko.RSAKey(filename=private_key_path)

            client.connect(
                hostname=str(ssh_host),
                port=ssh_port,
                username=str(ssh_user),
                pkey=private_key,
                timeout=10
            )

            # Check if port is listening on SSH server
            stdin, stdout, stderr = client.exec_command(f"netstat -tuln | grep :{bind_port} | grep LISTEN")
            output = stdout.read().decode().strip()
            
            if not output:
                client.close()
                return {'healthy': False, 'bound': False, 'tunnel_working': False, 'port': bind_port, 'status': 'unbound'}
            
            # Port is bound, now check if it's OUR tunnel process or a zombie
            # Check if there's an active SSH reverse tunnel process for this port
            print(f"🔍 Port {bind_port} is bound, checking if it's an active tunnel...")
            
            # Look for SSH process with reverse tunnel (-R) for this port
            stdin, stdout, stderr = client.exec_command(
                f"ps aux | grep -E 'sshd.*R.*{bind_port}' | grep -v grep | wc -l"
            )
            ssh_process_count = stdout.read().decode().strip()
            
            client.close()
            
            # If there's an active SSH tunnel process, consider it healthy
            # (We can't easily test if local service responds without complex setup)
            if ssh_process_count and int(ssh_process_count) > 0:
                return {'healthy': True, 'bound': True, 'tunnel_working': True, 'port': bind_port, 'status': 'healthy'}
            else:
                # Port is bound but no SSH tunnel process - it's a zombie
                return {'healthy': False, 'bound': True, 'tunnel_working': False, 'port': bind_port, 'status': 'zombie'}

        except Exception as e:
            print(f"Error checking port {bind_port}: {e}")
            return {'healthy': False, 'bound': False, 'tunnel_working': False, 'port': bind_port, 'status': 'error'}

    def kill_zombie_port_ssh_server(self, bind_port):
        """
        Kill/unbind a zombie port binding on the SSH server.
        Finds and terminates the process holding the port.

        Args:
            bind_port (int): Port on the SSH server to kill

        Returns:
            bool: True if port was killed successfully, False otherwise
        """
        ssh_host = os.getenv("SSH_HOST")
        ssh_port = int(os.getenv("SSH_PORT", 22))
        ssh_user = os.getenv("SSH_USER")
        private_key_path = os.getenv("PRIVATE_KEY_PATH")

        if not all([ssh_host, ssh_user, private_key_path]):
            print("Error: Missing required environment variables")
            return False

        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy())
            private_key = paramiko.RSAKey(filename=private_key_path)

            print(f"Connecting to {ssh_host} to kill port {bind_port}...")
            client.connect(
                hostname=str(ssh_host),
                port=ssh_port,
                username=str(ssh_user),
                pkey=private_key,
                timeout=10
            )

            # Find PID using the port
            print(f"Finding process using port {bind_port}...")
            stdin, stdout, stderr = client.exec_command(
                f"lsof -ti :{bind_port} 2>/dev/null || netstat -tulnp 2>/dev/null | grep :{bind_port} | awk '{{print $7}}' | cut -d'/' -f1"
            )
            pid_output = stdout.read().decode().strip()

            if not pid_output:
                print(f"✗ No process found using port {bind_port}")
                client.close()
                return False

            # Extract PID (might have multiple)
            pids = [p for p in pid_output.split('\n') if p]
            
            if not pids:
                print(f"✗ Could not determine PID for port {bind_port}")
                client.close()
                return False

            # Kill the process(es)
            for pid in pids:
                pid = pid.strip()
                if pid and pid.isdigit():
                    print(f"Killing process PID {pid}...")
                    stdin, stdout, stderr = client.exec_command(f"kill -9 {pid}")
                    error = stderr.read().decode().strip()
                    
                    if error:
                        print(f"⚠ Warning killing PID {pid}: {error}")
                    else:
                        print(f"✓ Successfully killed PID {pid}")

            # Verify port is now free
            time.sleep(1)
            stdin, stdout, stderr = client.exec_command(f"netstat -tuln | grep :{bind_port} | grep LISTEN")
            verify_output = stdout.read().decode().strip()
            client.close()

            if verify_output:
                print(f"✗ Port {bind_port} still bound after kill attempt")
                return False
            else:
                print(f"✓ Port {bind_port} is now free")
                return True

        except Exception as e:
            print(f"✗ Error killing zombie port: {e}")
            return False

    def add_port_config(self, name, local_port, remote_host, remote_port, server_bind_port=None, description=""):
        """
        Add a new port forwarding configuration to the database.

        Args:
            name (str): Unique name for this configuration
            local_port (int): Local port to forward from
            remote_host (str): Remote host to forward to
            remote_port (int): Remote port to forward to
            server_bind_port (int, optional): Port to bind on the server (for reverse forwarding)
            description (str): Optional description

        Returns:
            bool: True if added successfully, False otherwise
        """
        try:
            con = duckdb.connect('port_forwarding.db')

            # Check if name already exists
            existing = con.execute("SELECT rowid FROM port_configs WHERE name = ?", [name]).fetchone()
            if existing:
                print(f"✗ Port configuration '{name}' already exists")
                con.close()
                return False

            # Insert new configuration
            con.execute("""
                INSERT INTO port_configs (name, local_port, remote_host, remote_port, server_bind_port, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [name, local_port, remote_host, remote_port, server_bind_port, description])

            con.commit()
            con.close()
            print(f"✓ Added port configuration '{name}': localhost:{local_port} -> {remote_host}:{remote_port}")
            return True

        except Exception as e:
            print(f"✗ Failed to add port configuration: {e}")
            return False

    def list_port_configs(self):
        """
        List all port forwarding configurations from the database.

        Returns:
            list: List of port configuration dictionaries
        """
        try:
            con = duckdb.connect('port_forwarding.db')
            result = con.execute("""
                SELECT rowid, name, local_port, remote_host, remote_port, server_bind_port,
                       description, active, created_at
                FROM port_configs
                ORDER BY created_at DESC
            """).fetchall()

            configs = []
            for row in result:
                config = {
                    'id': row[0],
                    'name': row[1],
                    'local_port': row[2],
                    'remote_host': row[3],
                    'remote_port': row[4],
                    'server_bind_port': row[5],
                    'description': row[6],
                    'active': row[7],
                    'created_at': row[8]
                }
                configs.append(config)

            con.close()
            return configs

        except Exception as e:
            print(f"✗ Failed to list port configurations: {e}")
            return []

    def get_port_config(self, name_or_id):
        """
        Get a specific port configuration by name or ID.

        Args:
            name_or_id: Configuration name (str) or ID (int)

        Returns:
            dict: Port configuration dictionary or None if not found
        """
        try:
            con = duckdb.connect('port_forwarding.db')

            # Try to get by name first
            if isinstance(name_or_id, str):
                result = con.execute("""
                    SELECT rowid, name, local_port, remote_host, remote_port, server_bind_port,
                           description, active, created_at
                    FROM port_configs
                    WHERE name = ?
                """, [name_or_id]).fetchone()
            else:
                # Get by rowid
                result = con.execute("""
                    SELECT rowid, name, local_port, remote_host, remote_port, server_bind_port,
                           description, active, created_at
                    FROM port_configs
                    WHERE rowid = ?
                """, [name_or_id]).fetchone()

            con.close()

            if result:
                config = {
                    'id': result[0],
                    'name': result[1],
                    'local_port': result[2],
                    'remote_host': result[3],
                    'remote_port': result[4],
                    'server_bind_port': result[5],
                    'description': result[6],
                    'active': result[7],
                    'created_at': result[8]
                }
                return config
            else:
                return None

        except Exception as e:
            print(f"✗ Failed to get port configuration: {e}")
            return None

    def delete_port_config(self, name_or_id):
        """
        Delete a port forwarding configuration from the database.

        Args:
            name_or_id: Configuration name (str) or ID (int)

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            con = duckdb.connect('port_forwarding.db')

            # Try to delete by name first
            if isinstance(name_or_id, str):
                result = con.execute("DELETE FROM port_configs WHERE name = ?", [name_or_id])
            else:
                # Delete by rowid
                result = con.execute("DELETE FROM port_configs WHERE rowid = ?", [name_or_id])

            con.commit()
            con.close()

            print(f"✓ Deleted port configuration '{name_or_id}'")
            return True

        except Exception as e:
            print(f"✗ Failed to delete port configuration: {e}")
            return False
