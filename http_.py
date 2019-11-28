import asyncio, logging, sys

import aiohttp
from ssl import SSLError, SSLCertVerificationError

log = logging.getLogger(__file__)

# removing traceback for easier debugging
sys.tracebacklimit=0

class ConnectionInterrupted(Exception):
    pass 

session_ = aiohttp.ClientSession
timeout = aiohttp.ClientTimeout(10)

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
        async with session.get(url, timeout=timeout) as response:
            # raise exception
            if response.status != 200:
                response.raise_for_status()
            return await response.text(), url

    except aiohttp.client_exceptions.ClientConnectionError or aiohttp.client_exceptions.ServerDisconnectedError or aiohttp.client_exceptions.ClientOSError:
        log.warning("No internet connection")
        #raise ConnectionInterrupted("No internet connection")

    # BUG
    # SSL errors are specific to python 3.7
    # Either upgrade to 3.8 or https://github.com/aio-libs/aiohttp/issues/3535
    except aiohttp.client_exceptions.ClientResponseError or SSLError or SSLCertVerificationError:
        log.critical("Server response error")
    
    except asyncio.CancelledError or asyncio.TimeoutError:
        log.warning("Timeout exceded or task cancelled")


if __name__=="__main__":
    async def test():
        async with session_() as session:
            check = await fetch('http://google.com', session)
            if check:
                print("Connection OK")


            async for body, url in fetch_all(['http://indeed.co.uk', 'http://reed.co.uk'], session):
                print(f'Fetched {url}')

    asyncio.run(test())