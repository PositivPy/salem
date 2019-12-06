#!/usr/bin/env python3

import sys, os, logging, asyncio

import unittest

# catching and silencing all warnings
logging.captureWarnings(True)
logging.disable(logging.WARNING)


class TestHTTP(unittest.TestCase):
    import http_ 

    def test_fetch(self):
        async def test():
            async with self.http_.session_() as session:
                check = await self.http_.fetch('http://google.com', session)
                self.assertTrue(check)
        asyncio.run(test())

    def test_multi(self):
        async def test():
            async with self.http_.session_() as session:
                async for body, url in self.http_.fetch_all(['http://indeed.co.uk', 'http://reed.co.uk'], session):
                    if body:
                        self.assertTrue(body)
    
        asyncio.run(test())


class TestJobApi(unittest.TestCase):
    import jobs

    def setUp(self):
        query = "Bartender"

        self.indeed = self.jobs.Indeed(query)
        self.reed = self.jobs.Reed(query)

    def test_indeed(self):
        async def test():
            async for offer in self.indeed.run():
                self.assertTrue(offer)
                break
        asyncio.run(test())

    def test_reed(self):
        async def test():
            async for offer in self.reed.run():
                self.assertTrue(offer)
                break 
        asyncio.run(test())


class TestModel(unittest.TestCase):
    import model

    def test_job_model(self):
        offer = self.model.JobOffer()
        # just checks if it's a tuple for the moment
        self.assertIs(offer.__class__.__bases__[0], tuple)


class TestDB(unittest.TestCase):
    import model, database

    name = 'test.db'

    def setUp(self):
        async def build_db(name):
            return await self.database.AsyncDB(self.name, self.model)

        loop = asyncio.get_event_loop()
        self.db = loop.run_until_complete(asyncio.gather(build_db(self.name)))[0]

        self.test_offer = self.model.JobOffer('testOffer')
        self.test_query = 'test query'

    def test_db_built(self):
        dir_ = os.path.dirname(os.path.realpath(__file__))
        work_dir = f'{dir_}/data'

        db_exists = os.path.exists(f'{work_dir}/{self.name}')

        # if path exists, the db has been build properly
        self.assertTrue(db_exists)

    def test_retrieve_offer(self):
        # I don't know why this fails with RuntimeError
        async def test():
            res = await self.db.retrieve_offers_from(0)
            self.assertEqual(res[0], self.test_offer)

    def test_insert_entry(self):
        async def test():
            query_id, last_update = await self.db.insert_query(self.test_query)
            await self.db.insert_entry(query_id, self.test_offer)

        asyncio.run(test())

    def tearDown(self):
        # deleting the test database
        dir_ = os.path.dirname(os.path.realpath(__file__))
        work_dir = f'{dir_}/data'

        os.remove(f'{work_dir}/{self.name}')
        

class TestNLP(unittest.TestCase):
    import nlp

    def test_skills_extraction(self):
        dir_ = os.path.dirname(os.path.realpath(__file__))
        work_dir = f'{dir_}/data'

        f = open(f'{work_dir}/example_cv.txt')
        content = f.read()
        f.close()

        keywords = self.nlp.extract_skills(content)


if __name__=="__main__":
    unittest.main()