#!/usr/bin/env python3
"""
PyManage - Port Management CLI Tool
Interactive panel for managing port forwarding configurations using Haruka.

Features:
  • Create port forwarding configurations
  • Update existing configurations
  • Delete configurations
  • View all configurations
  • Check port health
  • Auto-initialize database on startup
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from __init__ import Haruka

class PyManage:
    """Port management interface using Haruka class."""
    
    def __init__(self):
        """Initialize PyManage with Haruka instance and auto-init database."""
        self.haruka = Haruka()
        self.running = True
        
        # Auto-initialize database if it doesn't exist
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database is initialized before any operations."""
        if not os.path.exists('port_forwarding.db'):
            print("\n📦 Database not found - Initializing port_forwarding.db...")
            if self.haruka.init_port_forwarding_db():
                print("✓ Database initialized successfully\n")
            else:
                print("✗ Failed to initialize database\n")
    
    def display_header(self):
        """Display main menu header."""
        print("\n" + "="*60)
        print("         🔧 PYMANAGE - PORT FORWARDING MANAGER 🔧")
        print("="*60)
        print("\nOptions:")
        print("  [1] Create port configuration")
        print("  [2] List all configurations")
        print("  [3] Start tunnel")
        print("  [4] Update configuration")
        print("  [5] Delete configuration")
        print("  [6] Check port health")
        print("  [7] Kill zombie port")
        print("  [8] Test SSH connection")
        print("  [0] Exit")
        print("\n" + "-"*60)
    
    def create_port_config(self):
        """Create new port configurations in a loop."""
        print("\n" + "="*60)
        print("CREATE PORT CONFIGURATIONS")
        print("="*60)
        print("(Type 'cancel' at any prompt to return to main menu)\n")
        
        count = 0
        while True:
            try:
                print(f"\n--- Configuration #{count + 1} ---")
                name = input("\nConfiguration name (e.g., 'webserver'): ").strip()
                if name.lower() == 'cancel':
                    if count > 0:
                        print(f"\n✅ Created {count} configuration(s) before cancellation")
                    else:
                        print("\n⚠ No configurations created")
                    return
                if not name:
                    print("✗ Name cannot be empty")
                    continue
                
                local_port_input = input("Local port (where your service runs): ").strip()
                if local_port_input.lower() == 'cancel':
                    if count > 0:
                        print(f"\n✅ Created {count} configuration(s) before cancellation")
                    else:
                        print("\n⚠ No configurations created")
                    return
                local_port = int(local_port_input)
                
                bind_port_input = input("Bind port (public port on SSH server): ").strip()
                if bind_port_input.lower() == 'cancel':
                    if count > 0:
                        print(f"\n✅ Created {count} configuration(s) before cancellation")
                    else:
                        print("\n⚠ No configurations created")
                    return
                bind_port = int(bind_port_input)
                
                public_ip = input(f"Public IP (default: {os.getenv('SSH_HOST')}): ").strip()
                if public_ip.lower() == 'cancel':
                    if count > 0:
                        print(f"\n✅ Created {count} configuration(s) before cancellation")
                    else:
                        print("\n⚠ No configurations created")
                    return
                public_ip = public_ip or os.getenv('SSH_HOST')
                
                description = input("Description (optional, or 'cancel'): ").strip()
                if description.lower() == 'cancel':
                    if count > 0:
                        print(f"\n✅ Created {count} configuration(s) before cancellation")
                    else:
                        print("\n⚠ No configurations created")
                    return
                
                print(f"\n📝 Creating configuration:")
                print(f"  Name: {name}")
                print(f"  Local Port: {local_port}")
                print(f"  Bind Port: {bind_port}")
                print(f"  Public IP: {public_ip}")
                if description:
                    print(f"  Description: {description}")
                
                # Use local_port for both local and remote (simplified)
                success = self.haruka.add_port_config(
                    name=name,
                    local_port=local_port,
                    remote_host=public_ip,
                    remote_port=local_port,  # Same as local_port
                    server_bind_port=bind_port,
                    description=description
                )
                
                if success:
                    print("✓ Configuration created successfully!")
                    count += 1
                else:
                    print("✗ Failed to create configuration")
                
                # Ask if user wants to create another with clear options
                print("\nOptions after creating configuration:")
                print("  [1] Create another configuration")
                print("  [0] Return to main menu")
                choice = input("\nYour choice (1/0): ").strip().lower()
                if choice != '1' and choice != 'yes' and choice != 'y':
                    if count > 0:
                        print(f"\n✅ Created {count} configuration(s) total!")
                    break
            
            except ValueError as e:
                print(f"✗ Invalid input: {e}")
            except Exception as e:
                print(f"✗ Error creating configuration: {e}")
    
    def list_configurations(self):
        """List all port configurations in a table format."""
        print("\n" + "="*60)
        print("ALL CONFIGURATIONS")
        print("="*60)
        
        configs = self.haruka.list_port_configs()
        
        if not configs:
            print("\n📭 No configurations found")
            return
        
        print(f"\n📋 Found {len(configs)} configuration(s):\n")
        
        # Table header
        header = f"  {'ID':<3} {'Name':<15} {'Local':<8} {'Bind':<6} {'Public IP':<18} {'Desc':<15}"
        print(header)
        print("  " + "─"*75)
        
        # Table rows
        for config in configs:
            config_id = str(config['id'])
            name = config['name'][:14]
            local = str(config['local_port'])
            bind_port = str(config['server_bind_port'])
            public_ip = config['remote_host'][:17]
            desc = config['description'][:14] if config['description'] else "-"
            
            row = f"  {config_id:<3} {name:<15} {local:<8} {bind_port:<6} {public_ip:<18} {desc:<15}"
            print(row)
        
        print("  " + "─"*75)
        print(f"\n  📌 Format: localhost:local_port → public_ip:bind_port\n")
    
    def start_tunnel(self):
        """Start a reverse port forwarding tunnel for a configuration."""
        print("\n" + "="*60)
        print("START TUNNEL")
        print("="*60)
        
        # Get list of configurations
        configs = self.haruka.list_port_configs()
        
        if not configs:
            print("\n📭 No configurations found")
            print("Create a configuration first using option [1]")
            return
        
        # Display list
        print("\n📋 Available configurations:\n")
        for idx, config in enumerate(configs, 1):
            print(f"  [{idx}] {config['name']}")
            print(f"      Local: {config['local_port']} → Bind: {config['server_bind_port']}")
            if config['description']:
                print(f"      Desc: {config['description']}")
        
        try:
            # Get user choice
            choice = input(f"\nSelect configuration (1-{len(configs)}): ").strip()
            
            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(configs):
                print("✗ Invalid selection")
                return
            
            config = configs[int(choice) - 1]
            
            print(f"\n🚀 Starting tunnel for: {config['name']}")
            print(f"  Local: localhost:{config['local_port']}")
            print(f"  Bind Port: {config['server_bind_port']}")
            
            # Check port health first
            print(f"\n🔍 Checking port health before starting...")
            health = self.haruka.check_port_health_ssh_server(config['server_bind_port'])
            
            if health['status'] == 'zombie':
                print(f"⚠️  Found zombie binding on port {config['server_bind_port']}")
                cleanup = input("Clean up zombie port before starting? (yes/no): ").strip().lower()
                
                if cleanup == 'yes' or cleanup == 'y':
                    print("🔨 Cleaning up zombie port...")
                    success = self.haruka.kill_zombie_port_ssh_server(config['server_bind_port'])
                    if not success:
                        print("✗ Failed to cleanup zombie port")
                        return
                    print("✓ Zombie port cleaned")
                else:
                    print("❌ Cannot start tunnel with zombie port binding")
                    return
            
            # Ask for background mode
            background = input("\nRun in background? (yes/no): ").strip().lower()
            background_mode = background == 'yes' or background == 'y'
            
            print(f"\n⏳ Starting tunnel...")
            success = self.haruka.reverse_forward_tunnel(
                local_port=config['local_port'],
                bind_port=config['server_bind_port'],
                background=background_mode
            )
            
            if success:
                if background_mode:
                    print(f"\n✓ Tunnel started in background!")
                    print(f"  Public access: ssh_host:{config['server_bind_port']}")
                    print(f"  Local service: localhost:{config['local_port']}")
                else:
                    print(f"\n✓ Tunnel created (press Ctrl+C to stop)")
            else:
                print("\n✗ Failed to start tunnel")
        
        except Exception as e:
            print(f"✗ Error starting tunnel: {e}")
    
    def update_configuration(self):
        """Update an existing configuration with field selection."""
        print("\n" + "="*60)
        print("UPDATE CONFIGURATION")
        print("="*60)
        
        # Get list of configurations
        configs = self.haruka.list_port_configs()
        
        if not configs:
            print("\n📭 No configurations found to update")
            return
        
        # Display list
        print("\n📋 Available configurations:\n")
        for idx, config in enumerate(configs, 1):
            print(f"  [{idx}] {config['name']}")
            print(f"      Local: {config['local_port']} → Bind: {config['server_bind_port']}")
            if config['description']:
                print(f"      Desc: {config['description']}")
        
        try:
            # Get user choice
            choice = input(f"\nSelect configuration to update (1-{len(configs)}): ").strip()
            
            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(configs):
                print("✗ Invalid selection")
                return
            
            config = configs[int(choice) - 1]
            
            print(f"\n📝 Updating: {config['name']}")
            print(f"\nCurrent values:\n")
            print(f"  [1] Name: {config['name']}")
            print(f"  [2] Local Port: {config['local_port']}")
            print(f"  [3] Bind Port: {config['server_bind_port']}")
            print(f"  [4] Public IP: {config['remote_host']}")
            print(f"  [5] Description: {config['description'] or 'N/A'}")
            print(f"  [0] Save and finish")
            
            # Dictionary to store updates
            updates = {
                'name': config['name'],
                'local_port': config['local_port'],
                'server_bind_port': config['server_bind_port'],
                'remote_host': config['remote_host'],
                'description': config['description'] or ''
            }
            
            # Field update loop
            while True:
                field_choice = input("\nSelect field to update (0-5): ").strip()
                
                if field_choice == '0':
                    break
                elif field_choice == '1':
                    new_name = input(f"New name [{updates['name']}]: ").strip()
                    if new_name:
                        updates['name'] = new_name
                        print(f"✓ Name updated to: {new_name}")
                elif field_choice == '2':
                    try:
                        new_port = int(input(f"New local port [{updates['local_port']}]: ").strip())
                        updates['local_port'] = new_port
                        print(f"✓ Local port updated to: {new_port}")
                    except ValueError:
                        print("✗ Invalid port number")
                elif field_choice == '3':
                    try:
                        new_port = int(input(f"New bind port [{updates['server_bind_port']}]: ").strip())
                        updates['server_bind_port'] = new_port
                        print(f"✓ Bind port updated to: {new_port}")
                    except ValueError:
                        print("✗ Invalid port number")
                elif field_choice == '4':
                    new_ip = input(f"New public IP [{updates['remote_host']}]: ").strip()
                    if new_ip:
                        updates['remote_host'] = new_ip
                        print(f"✓ Public IP updated to: {new_ip}")
                elif field_choice == '5':
                    new_desc = input(f"New description [{updates['description']}]: ").strip()
                    if new_desc:
                        updates['description'] = new_desc
                        print(f"✓ Description updated to: {new_desc}")
                    else:
                        updates['description'] = ''
                        print("✓ Description cleared")
                else:
                    print("✗ Invalid option")
            
            # Show changes summary
            print(f"\n📋 Changes Summary:")
            changed = False
            if updates['name'] != config['name']:
                print(f"  Name: {config['name']} → {updates['name']}")
                changed = True
            if updates['local_port'] != config['local_port']:
                print(f"  Local Port: {config['local_port']} → {updates['local_port']}")
                changed = True
            if updates['server_bind_port'] != config['server_bind_port']:
                print(f"  Bind Port: {config['server_bind_port']} → {updates['server_bind_port']}")
                changed = True
            if updates['remote_host'] != config['remote_host']:
                print(f"  Public IP: {config['remote_host']} → {updates['remote_host']}")
                changed = True
            if updates['description'] != (config['description'] or ''):
                print(f"  Description: {config['description'] or 'N/A'} → {updates['description']}")
                changed = True
            
            if not changed:
                print("  No changes made")
                return
            
            confirm = input("\nConfirm changes? (yes/no): ").strip().lower()
            
            if confirm == 'yes' or confirm == 'y':
                # Delete old and create new
                print("\n🔄 Saving changes...")
                self.haruka.delete_port_config(config['id'])
                
                success = self.haruka.add_port_config(
                    name=updates['name'],
                    local_port=updates['local_port'],
                    remote_host=updates['remote_host'],
                    remote_port=updates['local_port'],
                    server_bind_port=updates['server_bind_port'],
                    description=updates['description']
                )
                
                if success:
                    print("\n✓ Configuration updated successfully!")
                else:
                    print("\n✗ Failed to update configuration")
            else:
                print("❌ Update cancelled")
        
        except ValueError as e:
            print(f"\n✗ Invalid input: {e}")
        except Exception as e:
            print(f"\n✗ Error updating configuration: {e}")
    
    def delete_configuration(self):
        """Delete a port configuration."""
        print("\n" + "="*60)
        print("DELETE CONFIGURATION")
        print("="*60)
        
        # Get list of configurations
        configs = self.haruka.list_port_configs()
        
        if not configs:
            print("\n📭 No configurations found to delete")
            return
        
        # Display list
        print("\n📋 Available configurations:\n")
        for idx, config in enumerate(configs, 1):
            print(f"  [{idx}] {config['name']}")
            print(f"      Local: {config['local_port']} → Bind: {config['server_bind_port']}")
            if config['description']:
                print(f"      Desc: {config['description']}")
        
        try:
            # Get user choice
            choice = input(f"\nSelect configuration to delete (1-{len(configs)}): ").strip()
            
            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(configs):
                print("✗ Invalid selection")
                return
            
            config = configs[int(choice) - 1]
            
            print(f"\n⚠️  About to delete:")
            print(f"  Name: {config['name']}")
            print(f"  Local: {config['local_port']}")
            print(f"  Bind Port: {config['server_bind_port']}")
            
            confirm = input("\nAre you sure? (yes/no): ").strip().lower()
            
            if confirm == 'yes' or confirm == 'y':
                success = self.haruka.delete_port_config(config['id'])
                if success:
                    print("✓ Configuration deleted successfully!")
                else:
                    print("✗ Failed to delete configuration")
            else:
                print("❌ Deletion cancelled")
        
        except Exception as e:
            print(f"✗ Error deleting configuration: {e}")
    
    def check_port_health(self):
        """Check health of a port on SSH server."""
        print("\n" + "="*60)
        print("CHECK PORT HEALTH")
        print("="*60)
        
        try:
            bind_port = int(input("\nEnter bind port to check: "))
            
            print(f"\n🔍 Checking port {bind_port}...")
            health = self.haruka.check_port_health_ssh_server(bind_port)
            
            print(f"\n📊 Port Health Report:")
            print(f"  Port: {health['port']}")
            print(f"  Status: {health['status'].upper()}")
            print(f"  Healthy: {'✓ Yes' if health['healthy'] else '✗ No'}")
            
            if health['status'] == 'healthy':
                print("\n✓ Port is actively listening and working properly")
            elif health['status'] == 'zombie':
                print("\n⚠️  ZOMBIE BINDING DETECTED!")
                print("  The port is still occupied but not accepting connections")
                print("  Suggest: Kill this zombie port and restart tunnel")
                
                kill = input("\nKill this zombie port now? (yes/no): ").strip().lower()
                if kill == 'yes':
                    success = self.haruka.kill_zombie_port_ssh_server(bind_port)
                    if success:
                        print("✓ Zombie port killed successfully!")
                    else:
                        print("✗ Failed to kill zombie port")
            else:
                print("\n❓ Port status unclear - check manually on SSH server")
        
        except ValueError:
            print("✗ Invalid port number")
        except Exception as e:
            print(f"✗ Error checking port health: {e}")
    
    def kill_zombie_port(self):
        """Kill a zombie port binding."""
        print("\n" + "="*60)
        print("KILL ZOMBIE PORT")
        print("="*60)
        
        try:
            bind_port = int(input("\nEnter bind port to kill: "))
            
            print(f"\n⚡ Attempting to kill port {bind_port}...")
            success = self.haruka.kill_zombie_port_ssh_server(bind_port)
            
            if success:
                print(f"✓ Port {bind_port} killed successfully!")
                print("  Port is now available for reuse")
            else:
                print(f"✗ Failed to kill port {bind_port}")
                print("  Port may already be free or require elevated privileges")
        
        except ValueError:
            print("✗ Invalid port number")
        except Exception as e:
            print(f"✗ Error killing port: {e}")
    
    def test_ssh_connection(self):
        """Test SSH connection."""
        print("\n" + "="*60)
        print("TEST SSH CONNECTION")
        print("="*60 + "\n")
        
        if self.haruka.test_ssh_connection():
            print("\n✓ SSH connection test passed!")
        else:
            print("\n✗ SSH connection test failed!")
    
    def run(self):
        """Main loop for the PyManage interface."""
        print("\n╔" + "="*58 + "╗")
        print("║" + " "*58 + "║")
        print("║" + "  🔧 WELCOME TO PYMANAGE - PORT FORWARDING MANAGER  🔧".center(58) + "║")
        print("║" + " "*58 + "║")
        print("╚" + "="*58 + "╝")
        
        while self.running:
            self.display_header()
            
            choice = input("Enter option (0-8): ").strip()
            
            if choice == '1':
                self.create_port_config()
            elif choice == '2':
                self.list_configurations()
            elif choice == '3':
                self.start_tunnel()
            elif choice == '4':
                self.update_configuration()
            elif choice == '5':
                self.delete_configuration()
            elif choice == '6':
                self.check_port_health()
            elif choice == '7':
                self.kill_zombie_port()
            elif choice == '8':
                self.test_ssh_connection()
            elif choice == '0':
                print("\n👋 Thank you for using PyManage. Goodbye!\n")
                self.running = False
            else:
                print("✗ Invalid option. Please try again.")
            
            if self.running and choice != '0':
                input("\nPress Enter to continue...")

def main():
    """Entry point for PyManage."""
    try:
        manager = PyManage()
        manager.run()
    except KeyboardInterrupt:
        print("\n\n👋 PyManage interrupted by user\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
