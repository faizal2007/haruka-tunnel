#!/usr/bin/env python3
"""
Test script for zombie port detection and cleanup functions.

This script demonstrates how to:
1. Check if a port on the SSH server has a zombie binding
2. Kill/cleanup zombie port bindings

Useful for troubleshooting when tunnels break but ports remain bound.
"""

import sys
import os

# Add parent directory to path to import Haruka
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from __init__ import Haruka

def test_zombie_port_detection():
    """Test detecting zombie port bindings."""
    print("\n" + "="*60)
    print("ZOMBIE PORT DETECTION TEST")
    print("="*60)
    
    haruka = Haruka()
    
    # Test port to check (you can modify this)
    test_port = 5000
    
    print(f"\n1. Checking health of port {test_port} on SSH server...")
    health = haruka.check_port_health_ssh_server(test_port)
    
    print(f"\nResult:")
    print(f"  Port: {health['port']}")
    print(f"  Status: {health['status']}")
    print(f"  Healthy: {health['healthy']}")
    
    if health['status'] == 'healthy':
        print(f"\n✓ Port {test_port} is actively listening and working properly")
    elif health['status'] == 'zombie':
        print(f"\n⚠ Port {test_port} has a ZOMBIE binding (port bound but tunnel broken)")
        print(f"  This means the port is still occupied but not actually accepting connections")
        print(f"  The tunnel process may have crashed or disconnected unexpectedly")
    else:
        print(f"\n✗ Error checking port health")

def test_zombie_port_cleanup():
    """Test killing zombie port bindings."""
    print("\n" + "="*60)
    print("ZOMBIE PORT CLEANUP TEST")
    print("="*60)
    
    haruka = Haruka()
    
    # Test port to cleanup (you can modify this)
    test_port = 5000
    
    print(f"\n1. Attempting to kill/cleanup zombie port {test_port}...")
    success = haruka.kill_zombie_port_ssh_server(test_port)
    
    if success:
        print(f"\n✓ Successfully killed zombie port {test_port}")
        print(f"  Port is now available for reuse")
    else:
        print(f"\n✗ Failed to kill zombie port {test_port}")
        print(f"  The port may already be free, or you may need elevated privileges on the SSH server")

def test_workflow():
    """Test a complete workflow: detect then cleanup."""
    print("\n" + "="*60)
    print("COMPLETE ZOMBIE PORT WORKFLOW TEST")
    print("="*60)
    
    haruka = Haruka()
    test_port = 5000
    
    print(f"\nWorkflow: Check port health → Kill if zombie → Verify cleanup")
    print(f"Target port: {test_port}\n")
    
    # Step 1: Check port health
    print("Step 1: Checking port health...")
    health = haruka.check_port_health_ssh_server(test_port)
    print(f"  Status: {health['status']}")
    
    # Step 2: If zombie, kill it
    if health['status'] == 'zombie':
        print(f"\nStep 2: Detected zombie binding - attempting cleanup...")
        success = haruka.kill_zombie_port_ssh_server(test_port)
        
        if success:
            print(f"  ✓ Cleanup successful")
            
            # Step 3: Verify cleanup
            print(f"\nStep 3: Verifying port is now free...")
            new_health = haruka.check_port_health_ssh_server(test_port)
            
            if new_health['status'] != 'zombie':
                print(f"  ✓ Port is now free and ready for reuse")
            else:
                print(f"  ✗ Port still has zombie binding after cleanup")
        else:
            print(f"  ✗ Cleanup failed")
    else:
        print(f"\nStep 2: Port is not a zombie")
        if health['status'] == 'healthy':
            print(f"  Port is actively listening - no cleanup needed")
        else:
            print(f"  Port status is unclear - check manually on SSH server")

def test_multiple_ports():
    """Test checking multiple ports at once."""
    print("\n" + "="*60)
    print("MULTIPLE PORT HEALTH CHECK TEST")
    print("="*60)
    
    haruka = Haruka()
    
    # Test multiple ports
    test_ports = [5000, 5001, 5002, 8000, 8001]
    
    print(f"\nChecking health of {len(test_ports)} ports:")
    print(f"Ports to check: {test_ports}\n")
    
    results = []
    for port in test_ports:
        health = haruka.check_port_health_ssh_server(port)
        results.append(health)
        
        status_icon = "✓" if health['healthy'] else "✗"
        print(f"  {status_icon} Port {port}: {health['status']}")
    
    # Summary
    healthy_count = sum(1 for r in results if r['healthy'])
    zombie_count = sum(1 for r in results if r['status'] == 'zombie')
    error_count = sum(1 for r in results if r['status'] == 'error')
    
    print(f"\nSummary:")
    print(f"  Healthy ports: {healthy_count}")
    print(f"  Zombie bindings: {zombie_count}")
    print(f"  Errors: {error_count}")
    
    if zombie_count > 0:
        print(f"\n⚠ Found {zombie_count} zombie binding(s) that may need cleanup")

def main():
    """Run all tests."""
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║     HARUKA ZOMBIE PORT DETECTION & CLEANUP TEST SUITE    ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    print("\nThis test suite demonstrates:")
    print("  • Detecting zombie port bindings on SSH server")
    print("  • Cleaning up/killing zombie ports")
    print("  • Workflow for detecting and recovering from port bind failures")
    print("  • Batch checking multiple ports at once")
    
    # Run tests
    test_zombie_port_detection()
    test_zombie_port_cleanup()
    test_workflow()
    test_multiple_ports()
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)
    print("\nUsage in your code:")
    print("""
  from __init__ import Haruka
  
  haruka = Haruka()
  
  # Check if a port has a zombie binding
  health = haruka.check_port_health_ssh_server(5000)
  if health['status'] == 'zombie':
      print("Found zombie binding - cleaning up...")
      haruka.kill_zombie_port_ssh_server(5000)
  
  # Or cleanup before starting new tunnel
  haruka.kill_zombie_port_ssh_server(5000)  # Safe to call even if port is free
  haruka.reverse_forward_tunnel(3000, 5000, background=True)
    """)
    print("\n")

if __name__ == "__main__":
    main()
