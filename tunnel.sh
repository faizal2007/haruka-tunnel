#!/bin/bash
##  sshd_config at server required
##  GatewayPorts yes

kill_tunnel() {
    while IFS= read -r line
    do
        if [[ -z $(ps -ef | grep "$line"| grep -v grep) ]]
        then
            echo -e "\e[46m No tunnel to kill"
        else
            echo -e "\e[41m Kill $line"
            ps -ef | grep "$line"| grep -v grep| awk '{print $2}'| xargs kill -9
        fi
    done < $1
}

activate_tunnel() {
    while IFS= read -r line
    do
        if [[ -z $(ps -ef | grep "$line"| grep -v grep) ]]
        then
            echo -e "\e[44m Activate $line"
            $line
        else
            echo -e "\e[42m Active $line"
        fi
    done < "$1"
}

BASE=$(dirname $0)
LIST_TUNNEL="$BASE/list.tunnel"

echo -e "\e[49m \e[39m"
#activate_tunnel $LIST_TUNNEL
if [[ $1 == "kill" ]]
then
    kill_tunnel $LIST_TUNNEL
else
    activate_tunnel $LIST_TUNNEL
fi 

echo -e "\e[49m \e[39m"

