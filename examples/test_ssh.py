import paramiko
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_ssh_connection():
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
            timeout=10  # 10 second timeout
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

if __name__ == "__main__":
    success = test_ssh_connection()
    exit(0 if success else 1)