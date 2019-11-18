#!/usr/bin/env python3

import asyncio

import controller
   

if __name__=="__main__":
    app = asyncio.run(controller.App())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app.run()

    
