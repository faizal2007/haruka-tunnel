#!/bin/bash
##  sshd_config at server required
##  GatewayPorts yes

if [ -f .env ]; then
    source .env
    cd $HARUKA_HOME

    if [ "$1" == "start" ]; then
        # Start the service
        if [[ $PYTHON_BIN == /* ]]; then
            # if start with backslash script will assume python is outside haruka_home
            $PYTHON_BIN $HARUKA_HOME/tunneld.py
        else
            # start with no backslash script will assume python inside haruka_home
            $HARUKA_HOME/$PYTHON_BIN $HARUKA_HOME/tunneld.py
        fi
    elif [ "$1" == "stop" ]; then
        ps -ef | grep "tunnel" | grep -v "grep" | grep -v "./tunnel.sh stop" | awk '{print "Killing process", $2, "(", $10, ")"; system("kill -9 " $2)}'
    elif [ "$1" == "status" ]; then
        ps -ef | grep "tunnel" | grep -v "grep" | grep -v "./tunnel.sh status" | awk '{print "Tunnel process", $2, "(", $10, ")"}'
    else
        echo "Usage: $0 [start|stop|status]"
    fi
fi
