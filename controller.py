#!/usr/bin/env python3

import sys, collections.abc, asyncio, aiostream, logging, datetime

import database, views, jobs, nlp, model

log = logging.getLogger(__file__)


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
        self.db = await database.AsyncDB("query-offer.db", model)
        self.api = jobs.Interface                   # Dfferent interface too
        self.nlp = nlp
        self.view = views.WebView(self.search)       # passing self.search as a callback to view

    def run(self):
        self.view.start()

    async def search(self, query, location):
        """ Display search results """
        original_query = query

        # TODO : in a separate ArgumentParser
        # parsing the query for filters and add words
        query, filter = self.parse_filters(original_query)
        parsed_queries = self.flatten(self.parse_add_word(query))

        log.info(f'Query: {parsed_queries} Filter: {filter}')

        to_scrape = []
        for query in parsed_queries:
            query_id, last_update = await self.db.insert_query(query)

            if not last_update:
                # the query is new
                to_scrape.append((query_id, query))
            else:
                # check if query should be scraped again 
                last_update = datetime.datetime.strptime(last_update, '%Y-%m-%d %H:%M:%S')
                now = datetime.datetime.now()
                diff = now - last_update

                # if last update > 1h
                if diff > datetime.timedelta(1):
                    # scrape again
                    # TODO: the seen urls of the scrapers should be filled now 
                    to_scrape.append((query_id, query))
                else:

                    all_offers = await self.db.retrieve_offers_from(query_id)
                    for offer in all_offers:
                        yield offer

        log.debug(f'Queries to scrape : {to_scrape}')

        async for (id_, offer) in self.scrape(to_scrape, 1, location):
            # put all the offers on database waiting list
            log.debug(f'Offer {offer.title} from QueryID {id_} Scraped')
            if offer:
                if filter:
                    found = 0
                    for w in filter:
                        title = offer.title
                        title = title.lower()
                        if w in title:
                            found += 1
                    if not found:
                        yield offer
                else:
                    yield offer

                # saving offer in db 
                try:
                    await self.db.insert_entry(id_, offer)
                except Exception as e:
                    log.error(e)

    async def scrape(self, queries, depth=1, location='London'):
        """ Run the scraper for each query in queries
        Inserts the results into database """
        log.info("Scraping started")
        log.debug(f'Queries : {queries}')

        # create worker coroutines for each queries
        coros = [self.api(id, query=q, depth=depth, location=location).run() for (id, q) in queries]

        # merge these async generators into a single stream
        async for res in aiostream.stream.merge(*coros):
            query_id, offer = res
            log.debug(f'Got results from scraping query {query_id}, {offer.title}')
            if offer:
                # analyse the offer
                analysed = self.nlp.analyse(offer)
                yield query_id, analysed


    async def retrieve(self, query, location):
        """ Retrieve results from database """
        raise NotImplementedError

##### TODO : move all of this to an argument parser ####
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
        Essentialy creating multiple queries for each add words
        ie: junior developer +analyst = [junior developer, junior analyst]
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