#!/bin/bash
# Test Zombie Port Cleanup Workflow

echo "🧪 ZOMBIE PORT CLEANUP TEST"
echo "=" * 50

# Step 1: Check if we have configurations
echo "Step 1: Checking existing configurations..."
if [ ! -f "port_forwarding.db" ]; then
    echo "⚠️  No database found. Creating test configuration..."
    echo "You need to create a port config first. Run:"
    echo "  ./pymanage.py"
    echo "  [1] Create port configuration"
    echo "Then run this test again."
    exit 1
fi

# Step 2: Show current configs
echo -e "\nStep 2: Current configurations:"
python3 -c "
from __init__ import Haruka
haruka = Haruka()
configs = haruka.list_port_configs()
for config in configs:
    print(f'  • {config[\"name\"]}: {config[\"local_port\"]} → {config[\"server_bind_port\"]}')
"

echo -e "\n💡 ZOMBIE TESTING METHODS:"
echo "Method A: Quick Zombie Test"
echo "  1. ./simulate_zombie.py single 8080 10"
echo "  2. Wait 10 seconds for zombie state"
echo "  3. ./pytunnel.py (should detect and cleanup)"

echo -e "\nMethod B: Multiple Zombies"
echo "  1. ./simulate_zombie.py multiple 8080,9090,7070"
echo "  2. Wait for zombie state"
echo "  3. ./pytunnel.py (should cleanup all)"

echo -e "\nMethod C: Manual Kill Test"
echo "  1. ./pytunnel.py &"
echo "  2. Note PID and let it run briefly"
echo "  3. kill -9 <PID>"
echo "  4. ./pytunnel.py (should cleanup zombie)"

echo -e "\nMethod D: Test with Non-existent Config Port"
echo "  1. Create config with port 8999"
echo "  2. ./simulate_zombie.py single 8999"
echo "  3. ./pytunnel.py"

echo -e "\n🔍 VERIFICATION COMMANDS:"
echo "  # Check SSH server port bindings:"
echo "  ssh root@\$SSH_HOST 'netstat -tlnp | grep :8080'"
echo ""
echo "  # Check zombie processes:"
echo "  ssh root@\$SSH_HOST 'ps aux | grep ssh'"
echo ""
echo "  # Manual cleanup if needed:"
echo "  ssh root@\$SSH_HOST 'pkill -f \"ssh.*R.*8080\"'"

echo -e "\n▶️  Ready to test! Choose a method above."