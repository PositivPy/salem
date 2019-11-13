import aiohttp
import asyncio

"""
Async HTTP client.
fetch_all() is an async generator
"""

async def fetch(url, session):
    if session is None:
        session = aiohttp.ClientSession()
    async with session.get(url) as response:
        # raise exception
        if response.status != 200:
            response.raise_for_status()
        return await response.text()

async def fetch_single(url):
    print(f'Fetching {url}')
    async with aiohttp.ClientSession() as session:
        return await fetch(url, session)

async def fetch_all(urls):
    # open session
    print(f'Fetching offers...')
    async with aiohttp.ClientSession() as session:
        # goup all the coroutine in a list
        workers = [fetch(url, session) for url in urls]
        # yiel items as they complete
        for first_completed in asyncio.as_completed(workers):
            yield await first_completed
