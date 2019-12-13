#!/usr/bin/env python3

import sys, logging, asyncio, argparse

from . import controller

def parse_args(argv):
    parser = argparse.ArgumentParser(prog='salem',
            description='Salem job agregator and job market analysis.')

    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('-h', '--help', action='help',
            help='Shows this help message and exist.')

    parser.add_argument('-v', '--verbose', action='count', default=0,
            help='Increase verbosity output up to 3.')

    parser.add_argument('-c', '--cli', action='store_true',
            help='Command line only, else salem will run as a web app.')

    parser.add_argument('-r', '--report', action='store_true',
            help='Outputs a report on all queries in database')
    return parser.parse_args(argv)

def set_logger(args):
    ''' Set logging levels from arguments '''

    logging.basicConfig(
        level=logging.NOTSET,
        format='%(asctime)s %(name)s \t\t   %(levelname)-7s %(message)s',
        datefmt='%m-%d %H:%M:%S')

    root_logger = logging.getLogger()

    sql_log = logging.getLogger('aiosqlite')
    http_log = logging.getLogger('aiohttp')
    async_log = logging.getLogger('asyncio')

    sql_log.disabled = True
    http_log.disabled = True
    async_log.disabled = True

    if args.verbose == 0:
        root_logger.disabled = True

    if args.verbose == 1:
        root_logger.setLevel(logging.INFO)
        root_logger.info('Info active')

    if args.verbose >= 2:
        root_logger.setLevel(logging.DEBUG)
        root_logger.debug('Debug active')

    if args.verbose == 3:
        # full debug mode
        sql_log.disabled = False
        http_log.disabled = False
        async_log.disabled = False
        root_logger.debug('Debug active for aiosqlite and aiohttp')

    return root_logger

def run(args):
    app = asyncio.run(controller.App())
    # new loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if not args.cli:
        app.run()
    elif args.cli:
        app.search("bartender")

def main(argv=sys.argv[1:]):

    args = parse_args(argv)

    root_logger = logging.getLogger()
    sql_log = logging.getLogger('aiosqlite')
    http_log = logging.getLogger('aiohttp')
    async_log = logging.getLogger('asyncio')

    root_logger.disabled = True
    sql_log.disabled = True
    http_log.disabled = True
    async_log.disabled = True
    #log = set_logger(args)

    run(args)

if __name__ == "__main__":
    main()
