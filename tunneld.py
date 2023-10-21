#!/usr/bin/env python

import subprocess, os, sys, datetime, re

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
    # Define a regular expression pattern to match two segments separated by ":"
    pattern = re.compile(r'^\d+:\d+$')

    # Check if list_port.conf exists
    if not os.path.exists(f'{current_path}/list_port.conf'):
        # If the file doesn't exist, create it with default content
        with open(f'{current_path}/list_port.conf', 'w') as file:
            file.write('8443:443\n22023:22\n8080:80\n')  # Add default content

    full_path_script = os.path.join(current_path, script_name)

    # Read and validate the list_port.conf file
    valid_ports = []

    with open('list_port.conf', 'r') as file:
        for line in file:
            line = line.strip()  # Remove leading/trailing whitespace
            if pattern.match(line):
                valid_ports.append(line)
            else:
                print(f"Invalid line in list_port.conf: {line}")

    # Create the tunnels array based on valid port configurations
    tunnels = [{"command": [python_bin, full_path_script, port]} for port in valid_ports]

    for tunnel in tunnels:
        start_tunnel(tunnel["command"])

if __name__ == "__main__":
    main()
