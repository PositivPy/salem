import asyncio, logging

import aiohttp
from ssl import SSLError, SSLCertVerificationError

log = logging.getLogger(__file__)

"""
Async HTTP client.
fetch_all() is an async generator
"""

class ConnectionInterrupted(Exception):
    pass 

session_ = aiohttp.ClientSession

count = 0

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
    global count
    count += 1
    
    log.debug(f'Fetching {count}')

    try:
        async with session.get(url) as response:
            # raise exception
            if response.status != 200:
                response.raise_for_status()
            return await response.text(), url

    except aiohttp.client_exceptions.ClientConnectorError or aiohttp.client_exceptions.ServerDisconnectedError:
        log.critical("No internet connection")
        return

    # TODO : 
    # SSL errors are specific to python 3.7
    # Either upgrade to 3.8 or https://github.com/aio-libs/aiohttp/issues/3535
    except aiohttp.client_exceptions.ClientResponseError or SSLError or SSLCertVerificationError:
        log.critical("Server response error")
        return ConnectionInterrupted
        