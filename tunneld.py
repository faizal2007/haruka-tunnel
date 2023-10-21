#!/usr/bin/env python

import subprocess, os, sys, datetime

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
    # Get the current date and time
    current_datetime = datetime.datetime.now()
    # Format and print the current date and time
    now = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # Start the tunnel in the background
    process = subprocess.Popen(tunnel_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, close_fds=True)
    # Change the name of the subprocess
    print(f"{now} : Tunnel started. {sanitized_tunnel_name}")

def main():
    python_bin = sys.executable
    current_path = os.getcwd()
    script_name = "pytunnel.py"
    full_path_script = os.path.join(current_path, script_name)
    # Define tunnel configurations and PID file names
    tunnels = [
        {"command": [python_bin, full_path_script, "8443:443"]},
        {"command": [python_bin, full_path_script, "22023:22"]}
    ]

    for tunnel in tunnels:
        start_tunnel(tunnel["command"])

if __name__ == "__main__":
    main()
