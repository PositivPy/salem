#!/usr/bin/env python3

import sys, os, collections, asyncio, logging

import aiosqlite, models 
from aiosqlite import IntegrityError

log = logging.getLogger(__file__)

# disable traceback
#sys.tracebacklimit=0


class AsyncDB(models.aioObject):
    """ Async aiosqlite database """
    
    async def __init__(self, name, model):
        # get current dir
        dir = dir = os.path.dirname(os.path.realpath(__file__))
        # build database dir 
        self.name = f'{dir}/data/{name}' 
        self.model = model.JobOffer
    
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

        # the offer table is created from the model's fields and name directly 
        # see model.py for more information 
        await self.cursor.execute("CREATE TABLE IF NOT EXISTS %s (%s, PRIMARY KEY (%s))" \
                                % (self.model.__name__,", ".join(self.model._fields), ", ".join(
                                    self.model._fields[:3])))   

        await self.cursor.execute('''CREATE TABLE if not exists QUERY_TO_OFFER (
                                        offer_id INTEGER,
                                        query_id INTEGER,
                                        FOREIGN KEY(offer_id) REFERENCES OFFERS(rowid),
                                        FOREIGN KEY(query_id) REFERENCES QUERIES(rowid),
                                        PRIMARY KEY (offer_id, query_id))
                                ''')

        return await self.con.commit()

    async def insert_entry(self, query_id, offer):
        """ Insert the offer and link it's id to the query's id in QUERY_TO_OFFER """

        log.info(f"Saving Query: {query_id} Offer: {offer.title}")

        offer_id = await self.insert_offer(offer)

        try:
            async with aiosqlite.connect(self.name) as self.con:
                self.cursor = await self.con.cursor()
                await self.cursor.execute('''INSERT or IGNORE into QUERY_TO_OFFER VALUES (?, ?) ;''', (offer_id, query_id))
                await self.con.commit()
                log.debug("Done inserting")

        except Exception as e:
            log.error("Error inserting entry")

    @work
    async def insert_query(self, query):
        """ Inserting a query in the database and increment count 
        ::return:: row_id, last_update (None if new)"""
        # is the query in the database ?
        await self.cursor.execute('''SELECT rowid, count, last_update from QUERIES where string = ? ;''', (query,))
        try:
            # the query exist in the database
            row_id, count, last_update = await self.cursor.fetchone()

            # updating the count and last_seen
            count += 1
            await self.cursor.execute('''UPDATE QUERIES SET count = ?, last_update=CURRENT_TIMESTAMP WHERE rowid = ? ;''', (count, row_id,))
            await self.con.commit()
        
            log.debug(f'RowID: {row_id}, Last seen: {last_update}')

            return row_id, last_update

        except:
            # the query does not exist, thus create a new row
            await self.cursor.execute('''INSERT into QUERIES (string) VALUES (?) ;''', (query,))
            # we have a row_id now
            row_id = self.cursor.lastrowid
            await self.con.commit()

            log.debug(f'New query row ID: {row_id}')

            return row_id, None            

    @work
    async def insert_offer(self, offer):
        """ Insert offer into the database 
        ::return:: row_id """
        # check if the offer exists
        log.debug(f'Saving offer {offer.title}')
        try:
            # TODO: this is going to break as soon as the model changes 
            await self.cursor.execute('''INSERT into OFFERS VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ;''', 
                                        (offer.title, offer.company, offer.location, offer.minSalary,
                                        offer.maxSalary, f'{offer.description}', f'{offer.url}', f'{offer.skills}', 
                                        offer.matched))
            await self.con.commit()

            log.debug(f'Offer ID : {self.cursor.lastrowid}')
            return self.cursor.lastrowid

        except aiosqlite.IntegrityError:
            # already exists => fetch the rowid
            log.warning("Offer already exsists in database")
            await self.cursor.execute(f'''SELECT rowid from OFFERS where 
                                            (title=? AND company=? AND minSalary=?) ;''', (offer[0], offer[1], offer[3]))
            row_id = await self.cursor.fetchone()

            log.debug(f"Offer ID: {row_id}")
            return row_id[0]

        except AttributeError:
            log.error(f"Attribute error with : {offer}")
        
        except Exception as e:
            log.debug(f'Type error with offer : {offer}')
            log.error(e)
            
    async def retrieve_offers_from(self, query_id):

        # defining the return datatype
        def _namedtuple_factory(cursor, row):
            return self.model(*row)

        # create connection to database
        async with aiosqlite.connect(self.name) as self.con:
            # set the row factory to return the offers
            self.con.row_factory = _namedtuple_factory
            self.cursor = await self.con.cursor()

            # retrieve all the offers related to the query ID
            await self.cursor.execute(f'''SELECT offer_id from QUERY_TO_OFFER WHERE query_id='{query_id}' ;''')
            offer_ids = await self.cursor.fetchall()
            try:
                # finaly, select all the offers and yield named tuples
                await self.cursor.execute("SELECT * from OFFERS WHERE rowid IN {} ;".format(str(tuple([offer_id[0] for offer_id in offer_ids if offer_id[0] != None]))))
                return await self.cursor.fetchall()
            except:
                # the offer has a type problem
                raise TypeError
    
    @work 
    async def retrieve_all_queries(self):
        await self.cursor.execute('''SELECT rowid, * from QUERIES ;''')
        return await self.cursor.fetchall()


if __name__=="__main__":
    name = 'query-offer.db'
    # define async test function 
    async def test(name):
        db = await AsyncDB(name, model)

        res = await db.retrieve_offers_from(2)
        print(f"All Queries: {res}")
        
    # run test function
    asyncio.run(test(name))
