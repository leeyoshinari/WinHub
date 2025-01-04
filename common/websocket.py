#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import json
import traceback
from .ssh import SSH
from common.logging import logger
from mycloud.models import Servers


class WebSSH:
    def __init__(self, websocket):
        self.ws = websocket
        self.ssh = None

    async def receive(self, text_data=None):
        data = json.loads(text_data)
        if data.get('type') == "web":
            try:
                server = await Servers.get(id=data.get('id'))
                if server.host == data['host']:
                    ssh_args = {"width": int(data['cols']), "height": int(data['rows']), "auth": "pwd", "host": server.host,
                                "user": server.user, "password": server.pwd, "port": server.port, 'time': server.id}
                    await self.sshConnect(ssh_args)
            except:
                await self.ws.close()
                logger.error(traceback.format_exc())
        else:
            if data['code'] == 0:  # send data
                await self.ssh.django_to_ssh(data['data'])
            elif data['code'] == 2:  # close session
                await self.ssh.close()
            elif data['code'] == 1:  # setting terminal size
                self.ssh.resize_pty(cols=data['cols'], rows=data['rows'])

    async def sshConnect(self, ssh_args):
        self.ssh = SSH(websocket=self.ws)
        ssh_connect_dict = {
            'host': ssh_args.get('host'),
            'user': ssh_args.get('user'),
            'password': ssh_args.get('password'),
            'port': int(ssh_args.get('port')),
            'timeout': 30,
            'pty_width': ssh_args.get('width'),
            'pty_height': ssh_args.get('height'),
            'current_time': str(ssh_args.get('time'))
        }
        await self.ssh.connect(**ssh_connect_dict)

    async def disconnect(self):
        try:
            await self.ssh.close()
        except:
            pass
