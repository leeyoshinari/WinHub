#!/bin/sh
#port=$(cat config.conf | grep -E "^port" | awk -F '=' '{print $2}' | awk -F '\r' '{print $1}' | tr -d '\n' | xargs)
port=$winHubPort
if [ "$(uname)" = "Darwin" ] 
then
	lsof -i:${port}| grep "LISTEN"| awk -F ' ' '{print $2}'| xargs kill -9 
else
	ss -antp|grep $port |awk -F 'pid=' '{print $2 $3}'|awk -F ',' '{print $1, $4}' |xargs kill -9
fi
echo "Stop $port success ~"
