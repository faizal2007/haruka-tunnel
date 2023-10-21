#!/bin/bash
##  sshd_config at server required
##  GatewayPorts yes

HARUKA_HOME="/home/freakie/scripts/haruka-tunnel"
cd $HARUKA_HOME
PYTHON_BIN="venv/bin/python"

if [ "$1" == "start" ]; then
    # Start the service
    echo "$HARUKA_HOME/$PYTHON_BIN $HARUKA_HOME/tunneld.py"
    $HARUKA_HOME/$PYTHON_BIN $HARUKA_HOME/tunneld.py
elif [ "$1" == "stop" ]; then
    ps -ef | grep "tunnel" | grep -v "grep" | grep -v "./tunnel.sh stop" | awk '{print "Killing process", $2, "(", $10, ")"; system("kill -9 " $2)}'
else
    echo "Usage: $0 [start|stop]"
fi
