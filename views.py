#!/usr/bin/env python3

import asyncio, os, logging

import aiohttp.web

log = logging.getLogger(__file__)

class WebView:
    """ aiohttp server for website and api """
    
    def __init__(self, controller_interface):
        self.query_controller = controller_interface

        # need the dir for later
        self.dir = os.path.dirname(os.path.realpath(__file__))

        # loading the index html
        f = open(f'{self.dir}/web/index.html')
        self.index_html = f.read()
        f.close()
        
    def start(self):
        
        app = aiohttp.web.Application()
        app.add_routes([aiohttp.web.get('/search', self.socket),
                        aiohttp.web.get('/', self.index)])
        app.router.add_static('/static/', path=f'{self.dir}/web/')
        aiohttp.web.run_app(app)

    async def socket(self, request):
        # create a socket
        ws = aiohttp.web.WebSocketResponse()
        await ws.prepare(request)
        log.debug("Websocket open")

        # client sends the query as json as soon as the connection is open
        data = None
        async for msg in ws :
            data = msg.json()       #  = {'query' : _, 'location': _ }
            log.info("Query received")
            break
        try:
            async for offer in self.query_controller(data['query'], data['location']):
                # ws.send_json uses json.dumps()
                # TODO: something is going wrong here
                await ws.send_json(offer._asdict())
        except Exception as e:
            log.debug(e)
        finally:
            # close the websocket once done 
            await ws.close()
            log.debug("Websocket closed")
            log.info("Transmition Ended")

    async def index(self, request):
        log.info("Index requested")
        return aiohttp.web.Response(text=self.index_html, content_type='text/html')

