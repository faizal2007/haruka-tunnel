#!/usr/bin/env python

import subprocess, os

def is_process_running(pid):
    # Check if a process with the specified PID is running
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def sanitize_filename(filename):
    # Replace characters that are not allowed in filenames
    return filename.replace(":", "_")

def start_tunnel(tunnel_command):
    tunnel_name = os.path.basename(tunnel_command[2])
    sanitized_tunnel_name = sanitize_filename(tunnel_name)

    pid_file = os.path.join('run', f"{sanitized_tunnel_name}.pid")

    if os.path.exists(pid_file):
        with open(pid_file, 'r') as pid_file:
            existing_pid = int(pid_file.read())
        if is_process_running(existing_pid):
            print(f"Tunnel for {tunnel_name} is already running (PID: {existing_pid}).")
            return
        else:
            # Cleanup (delete) the old PID file if the process is not running
            os.remove(pid_file.name)

    # Start the tunnel in the background
    process = subprocess.Popen(tunnel_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, close_fds=True)
    print("Tunnel started.")

    # Write the PID to the specified file
    with open(pid_file.name, 'w') as pid_file:
        pid_file.write(str(process.pid))

def main():
    # Define tunnel configurations and PID file names
    tunnels = [
        {"command": ["python", "pytunnel.py", "8443:443"]},
        {"command": ["python", "pytunnel.py", "22023:22"]}
    ]

    for tunnel in tunnels:
        start_tunnel(tunnel["command"])

if __name__ == "__main__":
    main()
