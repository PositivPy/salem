import aiohttp
import asyncio

async def fetch(session, url):
    async with session.get(url) as response:
        if response.status != 200:
            response.raise_for_status()
        return await response.text()

async def fetch_all(session, urls):
    results = await asyncio.gather(*[asyncio.create_task(fetch(session, url))
                                   for url in urls])
    return results

async def main():
    urls = ['http://cnn.com',
            'http://google.com',
            'http://twitter.com']
    async with aiohttp.ClientSession() as session:
        htmls = await fetch_all(session, urls)
        print(htmls)

if __name__ == '__main__':
    asyncio.run(main())
