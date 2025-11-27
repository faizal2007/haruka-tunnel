#!/usr/bin/env python3
"""
Zombie Port Simulator - Create stale SSH tunnel bindings for testing pytunnel cleanup
"""

import sys
import os
import time
import signal
import threading
from __init__ import Haruka
from dotenv import load_dotenv

load_dotenv()

class ZombieSimulator:
    def __init__(self):
        self.haruka = Haruka()
        self.zombie_tunnels = []
        self.running = False
    
    def create_zombie_port(self, bind_port, duration=30):
        """Create a zombie port that will be abandoned after duration seconds."""
        print(f"🧟 Creating zombie port on {bind_port} for {duration} seconds...")
        
        try:
            # Start a reverse tunnel but don't keep it alive properly
            success = self.haruka.reverse_forward_tunnel(
                local_port=9999,  # Non-existent local service
                bind_port=bind_port,
                background=True
            )
            
            if success:
                print(f"✓ Zombie tunnel started on port {bind_port}")
                self.zombie_tunnels.append(bind_port)
                
                # Simulate zombie by stopping the local process but leaving SSH binding
                def abandon_tunnel():
                    time.sleep(duration)
                    print(f"💀 Abandoning tunnel on port {bind_port} (creating zombie)")
                    # The SSH binding will remain but local service is gone
                
                zombie_thread = threading.Thread(target=abandon_tunnel, daemon=True)
                zombie_thread.start()
                return True
            else:
                print(f"✗ Failed to create zombie on port {bind_port}")
                return False
                
        except Exception as e:
            print(f"✗ Error creating zombie port {bind_port}: {e}")
            return False
    
    def create_multiple_zombies(self, ports, duration=30):
        """Create multiple zombie ports."""
        print(f"\n🧟‍♂️ Creating {len(ports)} zombie ports...")
        
        for port in ports:
            success = self.create_zombie_port(port, duration)
            time.sleep(2)  # Small delay between creations
            
        print(f"\n✅ Zombie creation complete. Ports will become zombies in {duration} seconds.")
        print("💡 Now run: ./pytunnel.py to test zombie cleanup")
    
    def simulate_partial_zombie(self, bind_port):
        """Simulate a half-dead tunnel (SSH connected but local service down)."""
        print(f"🧟‍♀️ Creating partial zombie on port {bind_port}...")
        
        # Create tunnel to a non-existent local service
        success = self.haruka.reverse_forward_tunnel(
            local_port=65534,  # Unlikely to be used
            bind_port=bind_port,
            background=False  # Keep this one in foreground briefly
        )
        
        if success:
            print(f"✓ Partial zombie created - SSH binding exists but local service unavailable")
        
        return success
    
    def manual_zombie_instructions(self):
        """Show manual methods to create zombies."""
        print("\n📋 MANUAL ZOMBIE CREATION METHODS:\n")
        
        print("Method 1: Kill Python process (leaves SSH binding)")
        print("  1. Start: ./pytunnel.py")
        print("  2. Note the PID when it starts")
        print("  3. Kill process: kill -9 <PID>")
        print("  4. SSH binding remains active (zombie)")
        
        print("\nMethod 2: Network interruption")
        print("  1. Start tunnel on unreliable connection")
        print("  2. Disconnect network during tunnel operation")
        print("  3. Reconnect - SSH binding may be stale")
        
        print("\nMethod 3: SSH session crash")
        print("  1. Start tunnel normally")
        print("  2. On SSH server: pkill -f 'sshd.*R.*<port>.*localhost'")
        print("  3. Local process dies but binding persists briefly")
        
        print("\nMethod 4: Resource exhaustion")
        print("  1. Start many tunnels to exhaust SSH resources")
        print("  2. Some will fail partially, leaving zombies")
        
        print("\n💡 After creating zombies, test with:")
        print("  ./pytunnel.py  # Should detect and cleanup zombies")

def main():
    if len(sys.argv) < 2:
        print("🧟 ZOMBIE PORT SIMULATOR")
        print("=" * 50)
        print("\nUsage:")
        print("  python simulate_zombie.py <command> [options]")
        print("\nCommands:")
        print("  single <port> [duration]    - Create single zombie port")
        print("  multiple <port1,port2,...>  - Create multiple zombie ports")
        print("  partial <port>              - Create partial zombie")
        print("  manual                      - Show manual zombie methods")
        print("\nExamples:")
        print("  python simulate_zombie.py single 8080")
        print("  python simulate_zombie.py multiple 8080,9090,7070")
        print("  python simulate_zombie.py partial 8080")
        print("  python simulate_zombie.py manual")
        return
    
    simulator = ZombieSimulator()
    command = sys.argv[1].lower()
    
    if command == "single":
        if len(sys.argv) < 3:
            print("✗ Port required for single zombie")
            return
        
        port = int(sys.argv[2])
        duration = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        
        simulator.create_zombie_port(port, duration)
        
        # Keep script running to maintain zombie
        print(f"\n⏳ Keeping zombie alive for {duration} seconds...")
        print("Press Ctrl+C to stop early")
        try:
            time.sleep(duration + 5)  # Extra time for zombie state
        except KeyboardInterrupt:
            print("\n💀 Zombie simulation stopped")
    
    elif command == "multiple":
        if len(sys.argv) < 3:
            print("✗ Ports required (comma-separated)")
            return
        
        ports = [int(p.strip()) for p in sys.argv[2].split(',')]
        duration = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        
        simulator.create_multiple_zombies(ports, duration)
        
        # Keep running
        print(f"\n⏳ Maintaining zombies...")
        try:
            time.sleep(duration + 10)
        except KeyboardInterrupt:
            print("\n💀 All zombies stopped")
    
    elif command == "partial":
        if len(sys.argv) < 3:
            print("✗ Port required for partial zombie")
            return
        
        port = int(sys.argv[2])
        simulator.simulate_partial_zombie(port)
    
    elif command == "manual":
        simulator.manual_zombie_instructions()
    
    else:
        print(f"✗ Unknown command: {command}")
        print("Use: single, multiple, partial, or manual")

if __name__ == "__main__":
    main()