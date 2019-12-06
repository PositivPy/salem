#!/usr/bin/env python3

import sys, logging, asyncio, warnings

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
    import collections

    import model

    def test_job_model(self):
        offer = self.model.JobOffer()
        # just checks if it's a tuple for the moment
        self.assertIs(offer.__class__.__bases__[0], tuple)

if __name__=="__main__":
    unittest.main()