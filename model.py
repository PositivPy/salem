#!/usr/bin/env python3
import asyncio 
import aiosqlite
import scraper

class AsyncDB:
    """Async database via aiosqlite"""
    def __init__(self, name):
        self.scraper = scraper.Indeed(depth=1, location='London')
        self.name = name
        asyncio.run(self.open())

    async def open(self):
        con = await aiosqlite.connect(self.name)
        cursor = await con.cursor()
        await cursor.execute('''CREATE TABLE if not exists Jobs (
                        title, company, salary, location, type, 
                        date, description, url, apply_link, skills)''')
        await con.commit()
        await con.close()
        return con, cursor

    async def scrape_query(self, query):
        async with aiosqlite.connect(self.name) as db:
            async for offer in self.scraper.query(query):
                if offer is None:
                    pass 
                print(offer.title)
                f = f'INSERT INTO Jobs VALUES (\
                        ({offer.title}, {offer.company}, ({offer.salary}),\
                        ({offer.location}), ({offer.type_}), ({offer.date}),\
                        ({offer.txt}), ({offer.url}), ({offer.link}), ({offer.skills})'
                print(f)
                await db.execute(f)

if __name__=="__main__":
    import os 
    TEST = True

    name = "test.db"
    db = AsyncDB(name)
    asyncio.run(db.scrape_query("bartender"))

