#!/usr/bin/env python
import socket
import os
import select
import sys
import threading
import signal
import paramiko
from dotenv import load_dotenv
import argparse

# Load the environment variables from the .env file
load_dotenv()

def handler(chan, host, port):
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        print("Forwarding request to %s:%d failed: %r" % (host, port, e))
        return

    print(
        "Connected!  Tunnel open %r -> %r -> %r"
        % (chan.origin_addr, chan.getpeername(), (host, port))
    )
    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    chan.close()
    sock.close()


def reverse_forward_tunnel(server_port, remote_host, remote_port, transport):
    transport.request_port_forward("", server_port)
    while True:
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(
            target=handler, args=(chan, remote_host, remote_port)
        )
        thr.daemon = True
        thr.start()

def cleanup_tunnel(transport):
    try:
        transport.close()
    except Exception as e:
        print(f"Error while closing the tunnel: {e}")

def main():
    ssh_host = os.getenv("SSH_HOST")
    ssh_port = os.getenv("SSH_PORT")
    ssh_user = os.getenv("SSH_USER")
    # ssh_pass = ''
    private_key_path = os.getenv("PRIVATE_KEY_PATH")

    remote_bind_port = 8443  # port on server to forward
    forward_host = os.getenv("FORWARD_HOST")  # dest host to forward to
    forward_port = 443  # dest port to forward to

    parser = argparse.ArgumentParser(description="SSH Tunnel Manager")
    parser.add_argument("ports", help="The tunnel configuration (e.g., 8443:443)")

    args = parser.parse_args()
    remote_bind_port, forward_port = args.ports.split(":")
    #forward_host, forward_port = "localhost", int(forward_port)


    client = paramiko.SSHClient()
    client.load_system_host_keys()
    private_key = paramiko.RSAKey(filename=private_key_path)
    client.set_missing_host_key_policy(paramiko.WarningPolicy())

    try:
        client.connect(
            ssh_host,
            ssh_port,
            username=ssh_user,
            pkey=private_key
            #password=ssh_pass,
        )
    except Exception as e:
        print("*** Failed to connect to %s:%d: %r" % (ssh_host, ssh_port, e))
        sys.exit(1)

    print(
        "Now forwarding remote port %s to %s:%s ..."
        % (remote_bind_port, forward_host, forward_port)
    )
    try:
        reverse_forward_tunnel(remote_bind_port, forward_host, forward_port, client.get_transport())

    except KeyboardInterrupt:
        print("C-c: Port forwarding stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred during port forwarding: {e}")
        sys.exit(1)
    finally:
        cleanup_tunnel(client.get_transport())

if __name__ == "__main__":
    # Register a signal handler for Ctrl+C (SIGINT)
    signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(0))
    main()

