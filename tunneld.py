#!/usr/bin/env python

import subprocess, os, sys, datetime, re, psutil
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

def is_process_running(pid):
    # Check if a process with the specified PID is running
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def find_pid_by_command_line(target_cmdline):
    for process in psutil.process_iter(attrs=['pid', 'cmdline']):
        process_info = process.info
        if process_info['cmdline'] and re.match(target_cmdline, ' '.join(process_info['cmdline'])):
            return process_info['pid']
    return None

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
    haruka_home = os.getenv("HARUKA_HOME")
    script_name = "pytunnel.py"
    # Define a regular expression pattern to match two segments separated by ":"
    pattern = re.compile(r'^\d+:\d+$')

    # Check if list_port.conf exists
    if not os.path.exists(f'{haruka_home}/list_port.conf'):
        # If the file doesn't exist, create it with default content
        with open(f'{haruka_home}/list_port.conf', 'w') as file:
            file.write('8443:443\n22023:22\n8080:80\n')  # Add default content
    full_path_script = os.path.join(haruka_home, script_name)
    # Read and validate the list_port.conf file
    valid_ports = []

    with open(f'{haruka_home}/list_port.conf', 'r') as file:
        for line in file:
            line = line.strip()  # Remove leading/trailing whitespace
            if pattern.match(line):
                valid_ports.append(line)
            else:
                print(f"Invalid line in list_port.conf: {line}")

    # Create the tunnels array based on valid port configurations
    tunnels = [{"command": [python_bin, full_path_script, port]} for port in valid_ports]

    for tunnel in tunnels:
        target_cmdline = r".*/%s %s$" % (script_name, tunnel["command"][2])
        pid = find_pid_by_command_line(target_cmdline)

        if pid is None:
            start_tunnel(tunnel["command"])
        else:
            print(f'Tunnel process {pid} ( {tunnel["command"][2]} )')

if __name__ == "__main__":
    main()
