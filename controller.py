#!/usr/bin/env python3

import argparse
import sys
import model, scraper, views
import asyncio
from aiohttp import web

class aioObject(object):
    """ Inheriting this class allows you to define an async __init__.
    So you can create objects by doing something like 'await MyClass(params)'
    https://stackoverflow.com/questions/33128325/how-to-set-class-attribute-with-await-in-init
    """
    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self):
        pass

class Controller(aioObject):

    async def __init__(self):
        self.db = await model.AsyncDB("jobs.db")    # Different databases for job and item
        self.api = scraper.Indeed(depth=5)          # Possible to have multiple api
        self.template = views.TemplateEngine()

    def web_view(self):
        app = web.Application()
        app.add_routes([web.get('/', self.index),
                        web.get('/search/', self.search)])
        web.run_app(app)

    async def index(self, request):
        html = self.template.render_index()
        return web.Response(text=html, content_type='text/html')

    async def search(self, request):
        query = request.rel_url.query['q']
        offers = []
        async for offer in self.api.query(query):
            offers.append(offer)
            await self.db.insert(offer)
        offers.sort(key=lambda x: int(x.salary[0]), reverse=True)
        html = self.template.render_results(offers)
        return web.Response(text=html, content_type='text/html')

if __name__ == '__main__':
    c = asyncio.run(Controller())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    c.web_view()