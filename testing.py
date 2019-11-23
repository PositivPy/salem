#!/usr/bin/env python3

import os, collections, asyncio, logging

import aiosqlite
from aiosqlite import IntegrityError

log = logging.getLogger(__file__)

# TODO : move Offer namedtuple
Offer = collections.namedtuple('JobOffer', 'title company salary location \
                                         type_ date txt url link skills matched',
                                         defaults=(0,))

# TODO : move aioObject somewhere else
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

class AsyncDB(aioObject):
    """ Async aiosqlite database """
    
    async def __init__(self, name):
        # get current dir
        dir = dir = os.path.dirname(os.path.realpath(__file__))
        # build database dir 
        self.name = f'{dir}/data/{name}' 
    
        self.con = None
        self.cursor = None

        # create table on init
        await self.create_tables()

    def work(func):
        """ Async decorator: opening the database in a context manager before use """
        async def _wraper(*args):
            # decorator in class : extract self from function args
            self = args[0]
            # open connection in a context manager
            async with aiosqlite.connect(self.name) as self.con:
                self.cursor = await self.con.cursor()
                return await func(*args)
        return _wraper

    @work
    async def create_tables(self):
        """ Create the database's tables if they do not exist """
        await self.cursor.execute('''CREATE TABLE if not exists QUERIES (
                                        string TEXT UNIQUE,
                                        last_update TEXT DEFAULT CURRENT_TIMESTAMP,
                                        count INTEGER DEFAULT 1)
                                ''')

        await self.cursor.execute('''CREATE TABLE if not exists OFFERS (
                                        title TEXT,
                                        company TEXT, 
                                        location TEXT,
                                        min_£ INTEGER DEFAULT NULL,
                                        max_£ INTEGER DEFAULT 0, 
                                        description TEXT, 
                                        url TEXT, 
                                        skills TEXT DEFAULT NULL, 
                                        matched INTEGER DEFAULT NULL,
                                        PRIMARY KEY (title, company, min_£))
                                ''')   

        await self.cursor.execute('''CREATE TABLE if not exists QUERY_TO_OFFER (
                                        offer_id INTEGER NOT NULL,
                                        query_id INTEGER NOT NULL,
                                        FOREIGN KEY(offer_id) REFERENCES OFFERS(rowid),
                                        FOREIGN KEY(query_id) REFERENCES QUERIES(rowid),
                                        PRIMARY KEY (offer_id, query_id))
                                ''')

        return await self.con.commit()

    @work
    async def insert_entry(self, query_id, offer):
        log.debug(f"Saving Query: {query_id} Offer: {offer.title}")
        offer_id = await self.insert_offer(offer)
        query_id = await self.update_query(query_id)

        try:
            async with aiosqlite.connect(self.name) as self.con:
                self.cursor = await self.con.cursor()
                await self.cursor.execute('''INSERT into QUERY_TO_OFFER VALUES (?, ?) ;''', (offer_id, query_id))
                await self.con.commit()
        except aiosqlite.IntegrityError:
            log.error("Error saving query")
            pass

    @work
    async def update_query(self, id):
        await self.cursor.execute('''UPDATE QUERIES SET last_update=CURRENT_TIMESTAMP WHERE rowid = ? ;''', (id,))
        await self.con.commit()
        return id

    @work
    async def insert_query(self, query):
        """ Inserting a query in the database,
        return something if already in DB and increment count 
        ::return:: row_id of the query, last_update (None if new)"""
        # is the query in the database ?
        await self.cursor.execute('''SELECT rowid, count, last_update from QUERIES where string = ? ;''', (query,))
        
        try:
            row_id, count, last_update = await self.cursor.fetchone()
        except:
            row_id = None

        if not row_id:
            # create the row
            await self.cursor.execute('''INSERT into QUERIES (string) VALUES (?) ;''', (query,))
            # we have a row_id now
            row_id = self.cursor.lastrowid
            await self.con.commit()

            return row_id, None

        else:
            # TODO : increment the last_update with new/old as to keep the real value 
            # we increment the counter
            count += 1
            await self.cursor.execute('''UPDATE QUERIES SET count = ? WHERE rowid = ? ;''', (count, row_id,))
            await self.con.commit()
        
            log.debug(f'RowID: {row_id}, Last Updated: {last_update}')
            return row_id, last_update

    @work
    async def insert_offer(self, offer):
        """ Insert offer into the database 
        ::return:: row_id """
        # check if the offer exists
        try:
            await self.cursor.execute('''INSERT into OFFERS (title, company, location, min_£, description, url)
                                        VALUES (?, ?, ?, ?, ?, ?) ;''', (*offer,))
            await self.con.commit()

            return self.cursor.lastrowid

        except aiosqlite.IntegrityError:
            # already exists => fetch the rowid
            await self.cursor.execute(f'''SELECT rowid from OFFERS where 
                                            (title=? AND company=? AND min_£=?) ;''', (offer[0], offer[1], offer[3]))
            row_id = await self.cursor.fetchone()

            return row_id[0]

        except AttributeError:
            print(f"Attribute error with : {offer}")

    @work 
    async def retrieve_all_queries(self):
        await self.cursor.execute('''SELECT rowid, * from QUERIES ;''')
        res = await self.cursor.fetchall()
        print(res)

    @work
    async def retrieve_all_offers(self):
        await self.cursor.execute('''SELECT rowid, * from OFFERS ;''')
        res = await self.cursor.fetchall()
        print(res)

    @work
    async def retrieve_all_relation(self):
        await self.cursor.execute('''SELECT * from QUERY_TO_OFFER''')
        res = await self.cursor.fetchall()
        print(res)

if __name__=="__main__":
    import sys

    extension = '.db'

    name = ''
    try:
        name = sys.argv[1] + extension
    except IndexError:
        print("Name of the database as first argument")
        exit(1)

    # define async test function 
    async def test(name):
        db = await AsyncDB(name)
        log.info("Database created in /data")

        print("All Queries:")
        await db.retrieve_all_queries()
        print("All Offers")
        await db.retrieve_all_offers()
        print("All relations")
        await db.retrieve_all_relation()

    # run test function
    asyncio.run(test(name))
