#!/bin/sh
#ip=$(cat config.conf | grep -E "^host" | awk -F '=' '{print $2}' | awk -F '\r' '{print $1}' | tr -d '[:space:]')
#port=$(cat config.conf | grep -E "^port" | awk -F '=' '{print $2}' | awk -F '\r' '{print $1}' | tr -d '[:space:]')
ip=$winHubHost
port=$winHubPort
gunicorn main:app -b $ip:$port -k uvicorn.workers.UvicornWorker --timeout 30 --daemon
echo "start server success ~"
