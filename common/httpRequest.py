#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import aiohttp
import aiofiles
import asyncio
from typing import Optional


class HttpResponse:

    def __init__(self, *, url: str, status: int, headers: dict, text: str, content: bytes):
        self.url = url
        self.status_code = status
        self.headers = headers
        self.text = text
        self.content = content


class HttpClient:

    def __init__(self, timeout: int = 180, max_connections: int = 200, max_per_host: int = 50, retry: int = 2):
        self.timeout = timeout
        self.max_connections = max_connections
        self.max_per_host = max_per_host
        self.retry = retry

        self.session: Optional[aiohttp.ClientSession] = None
        self.connector: Optional[aiohttp.TCPConnector] = None
        self._lock = asyncio.Lock()

    async def start(self):
        async with self._lock:
            if self.session and not self.session.closed:
                return

            timeout = aiohttp.ClientTimeout(total=self.timeout)

            self.connector = aiohttp.TCPConnector(
                limit=self.max_connections,
                limit_per_host=self.max_per_host,
                ssl=False,
            )

            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=self.connector,
                raise_for_status=False,
            )

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def request(self, method: str, url: str, *, params=None, data=None, json=None, headers=None, **kwargs) -> HttpResponse:
        await self.start()
        for attempt in range(self.retry + 1):
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json,
                    headers=headers,
                    **kwargs,
                ) as resp:

                    text = await resp.text()
                    content = await resp.read()

                    return HttpResponse(
                        url=str(resp.url),
                        status=resp.status,
                        headers=dict(resp.headers),
                        text=text,
                        content=content,
                    )

            except Exception:
                if attempt >= self.retry:
                    raise
                await asyncio.sleep(0.5 * (attempt + 1))

    async def download(self, url: str, file_path: str, chunk_size: int = 1024, **kwargs) -> None:
        """
        流式下载文件
        :param url: 下载地址
        :param file_path: 保存路径
        :param chunk_size: 块大小
        """
        await self.start()
        for attempt in range(self.retry + 1):
            try:
                async with self.session.request(method="GET", url=url, **kwargs) as resp:
                    resp.raise_for_status()
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(chunk_size):
                            if chunk:
                                await f.write(chunk)
                    return
            except Exception:
                if attempt >= self.retry:
                    raise
                await asyncio.sleep(0.5 * (attempt + 1))

    async def get(self, url: str, **kwargs) -> HttpResponse:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> HttpResponse:
        return await self.request("POST", url, **kwargs)


# 全局单例
http = HttpClient()
