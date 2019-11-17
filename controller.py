#!/usr/bin/env python3

import argparse
import sys
import model, scraper, view
import asyncio
from aiohttp import web
import collections.abc
import aiostream

# TODO: 
# -> websocket
# -> move all the view stuff to view;
# -> check if query in db + last update (build relational db)  
# -> move aioObject somewhere else
# -> add logging (how did I manage so far?)
# -> add support for double quotes and | (maybe not necessary)
# -> add support for filtering skills
# -> web view face lift 
# -> add location to the search (default=London)

# To think about :
# -> auto resume (organise resume automaticaly based on the skills requirements)
# -> auto apply
# -> crontab 
# -> cli view (long live the cli)
# -> data analysis:
#       - most skills required
#       - median and average salary for the query
# -> delete results in web view ?

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
    """ Controlling the scraper's behaviors """
    async def __init__(self):
        self.db = await model.AsyncDB("jobs.db")    # Different databases for job and item
        self.api = scraper.Indeed(depth=2)          # Possible to have multiple api
        self.view = view.WebView(self.search)

    def run(self):
        self.view.run()

    async def search(self, query):
        """ Display search results """
        # fetching the query from the request's parameters
        original_query = query

        query, params = self.parse_filters(original_query)
        parsed_query = self.flatten(self.parse_add_word(query))

        async for offer in self.query_api(parsed_query):
            await self.db.insert(offer)
            if params:
                yes = 0
                for w in params:
                    title = offer.title
                    title = title.lower()
                    if w in title:
                        yes += 1
                if not yes:
                    yield offer
            else:
                yield offer

    async def query_api(self, queries):
        """ Query the scraper for each query extracted by parsed query """
        # TODO : probably move it to the scraper

        # create worker coroutines for each queries
        coros = [self.api.query(q) for q in queries]
        
        # merge these async generators into a single stream
        async for offer in aiostream.stream.merge(*coros):
            yield offer

    def flatten(self, x):
        """ Flatten a list of nested list of unknown depth to a simple list """
        if isinstance(x, collections.abc.Iterable) and not isinstance(x, str):
            return [a for i in x for a in self.flatten(i)]
        else:
            return [x]

    def parse_filters(self,query):
        """ Parsing query for -words """
        query = query.split()
        params = []
        s_query = []
        for word in query:     
            if '-' in word:
                # add the word to params without the - char
                params.append(word.replace('-',''))
                # remove word from the query
            else:
                s_query.append(word)
        return s_query, params

    def parse_add_word(self, query, result=None, params=None):
        """ Parsing the query string for +words """
        if not result:
            result = []
        if not params:
            params = []
        # try to split it on first run
        try:
            query = query.split()
        except:
            pass

        for word in query:
            if '+' in word:
                word_index = query.index(word)
                # remove the + char
                query[word_index] = query[word_index].replace('+', '')

                # current word is +word
                current_word = query[word_index]
                previous_word = query[word_index - 1]

                # query - +word 
                original_query = [word for word in query if word != previous_word]
                # query - word before +word
                added_query = [word for word in query if word != current_word]

                # parsing and returning both new query strings
                parsed_a = self.parse_add_word(added_query, result, params)
                parsed_o = self.parse_add_word(original_query, result, params)
                result.append(parsed_a)
                result.append(parsed_o)
                return result
        # flatten the query back to a string 
        queries = ' '.join(query)
        return queries, params

if __name__ == '__main__':
    c = asyncio.run(Controller())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    c.run()