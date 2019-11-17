#!/usr/bin/env python3

import sys, collections.abc, asyncio, aiostream

import model, view, scraper

# TODO: 
# BUG : There is a problem with the scraper not getting every pages 
# Could be related to session drops or the way the listing urls are generated

# -> add logging (how did I manage so far?)

# -> move nltk to controller
# -> compare query to db + last update (build relational db)  
# -> move aioObject somewhere else
# -> a way to remove doubles 
# -> add support for double quotes and | (maybe not necessary)
# -> add support for filtering skills
# -> web view face lift 

# To think about :
# -> auto resume (organise resume automaticaly based on the skills requirements)
# -> auto apply
# -> crontab 
# -> cli view (long live the cli)
# -> data analysis:
#       - most skills required
#       - median and average salary for the query

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

class App(aioObject):
    """ Controlling the app's behaviors """
    async def __init__(self):
        self.db = await model.AsyncDB("jobs.db")    # Different databases for job and item
        self.api = scraper.Indeed()          # Possible to have multiple api
        self.view = view.WebView(self.search)

    def run(self):
        self.view.run()

    async def search(self, query, location):
        """ Display search results """
        original_query = query

        # TODO : in a separate ArgumentParser
        # parsing the query for filters and add words
        query, filter = self.parse_filters(original_query)
        parsed_queries = self.flatten(self.parse_add_word(query))

        async for offer in self.scrape(parsed_queries, 1, location):
            if filter:
                yes = 0
                for w in filter:
                    title = offer.title
                    title = title.lower()
                    if w in title:
                        yes += 1
                if not yes:
                    yield offer
            else:
                yield offer

    async def scrape(self, queries, depth=1, location='London'):
        """ Run the scraper for each query in queries
        Inserts the results into database """
        # TODO : probably move it to the scraper

        # create worker coroutines for each queries
        coros = [self.api.get(query=q, depth=depth, location=location) for q in queries]
        
        # merge these async generators into a single stream
        async for offer in aiostream.stream.merge(*coros):
            # TODO : nltk should be here
            await self.db.insert(offer)
            yield offer

    async def retrieve(self, query, location):
        """ Retrieve results from database """
        raise NotImplementedError

    # TODO : move all of this to an argument parser
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

    def parse_add_word(self, query, result=None):
        """ Parsing the query string for +words 
        Essentialy creating multiple queries for each words
        ie: junior developer + analyst = [junior developer, junior analyst]
        """
        if not result:
            result = []
        # try to split it on first run
        try:
            query = query.split()
        except:
            pass

        for word in query:
            if '+' in word:
                index = query.index(word)
                # remove the + char
                query[index] = query[index].replace('+', '')

                # current word is +word
                current_word = query[index]
                previous_word = query[index - 1]

                # query - +word 
                original_query = [word for word in query if word != previous_word]
                # query - previous_word 
                added_query = [word for word in query if word != current_word]

                # parsing and returning both new query strings
                parsed_a = self.parse_add_word(added_query, result)
                parsed_o = self.parse_add_word(original_query, result)
                result.append(parsed_a)
                result.append(parsed_o)
                return result
        # flatten the query back to a string 
        queries = ' '.join(query)
        return queries

if __name__ == '__main__':
    app = asyncio.run(App())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app.run()