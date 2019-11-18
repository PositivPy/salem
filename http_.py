import aiohttp
import asyncio

"""
Async HTTP client.
fetch_all() is an async generator
"""

class ConnectionInterrupted(Exception):
    pass 

max_connection = 100
sem = asyncio.Semaphore(max_connection)

connector_ = aiohttp.TCPConnector(keepalive_timeout=None, limit=None,
                                verify_ssl=False)
session_ = aiohttp.ClientSession

async def fetch_all(urls, session):
    """
    Fetch multiple urls
    urls is a iterable (list or generator)
    ::async yield:: body, url
    """ 
    workers = [fetch(url, session) for url in urls]
    # yiel items as they complete
    for first_completed in asyncio.as_completed(workers):
        yield await first_completed

async def fetch(url, session):
    """
    Fetch single url
    ::async return:: body, url
    """
    try:
        async with session.get(url) as response:
            # raise exception
            if response.status != 200:
                response.raise_for_status()
            return await response.text(), url
    except aiohttp.client_exceptions.ClientConnectorError:
        raise ConnectionInterrupted("No internet connection")
    except aiohttp.client_exceptions.ClientResponseError:
        return "Server error", "500" 
