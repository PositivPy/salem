import aiohttp
import asyncio

"""
Async HTTP client.
fetch_all() is an async generator
"""

class ConnectionInterrupted(Exception):
    pass 


async def fetch_single(url):
    """
    Public function to fetch a single url.
    ::async return:: body
    """
    # open session
    async with aiohttp.ClientSession() as session:
        return await _fetch(url, session)

async def fetch_all(urls):
    """
    Public function to fetch multiple urls
    urls is a iterable (list or generator)
    ::async yield:: body
    """ 
    # open session
    async with aiohttp.ClientSession() as session:
        # goup all the coroutine in a list
        workers = [_fetch(url, session) for url in urls]
        # yiel items as they complete
        for first_completed in asyncio.as_completed(workers):
            yield await first_completed

async def _fetch(url, session):
    try:
        async with session.get(url) as response:
            # raise exception
            if response.status != 200:
                response.raise_for_status()
            res = await response.text()
            return res, url
    except aiohttp.client_exceptions.ClientConnectorError:
        raise ConnectionInterrupted("No internet connection")

