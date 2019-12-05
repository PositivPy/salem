#!/usr/bin/env python3

import sys, logging, asyncio

import controller

def main(argv=sys.argv[1:]):
    level = logging.DEBUG
    #level = logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s %(name)s \t\t   %(levelname)-7s %(message)s',
        datefmt='%m-%d %H:%M:%S')

    sql_log = logging.getLogger('aiosqlite').setLevel(logging.INFO)

    logger = logging.getLogger(__file__)

    logger.info(f'Arguments: {argv}')
    run()

def run():
    app = asyncio.run(controller.App())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app.run()

if __name__ == "__main__":
    main()
