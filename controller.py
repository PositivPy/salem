#!/usr/bin/env python3

import sys, collections.abc, asyncio, aiostream, logging, datetime

import database, views, jobs, nlp, models

log = logging.getLogger(__file__)

class App(models.aioObject):
    """ Controlling the app's behaviors """

    async def __init__(self):
        self.db = await database.AsyncDB("query-offer.db", models)
        self.api = jobs.Interface
        self.nlp = nlp
        # passing self.search as a callback to view
        self.view = views.WebView(self.search)

    def run(self):
        ''' Run in web view '''
        self.view.start()

    async def search(self, query, location):
        ''' Search and stores offers '''
        # parsing the query for filters and add words
        original_query = query 
        query, filters = self.parse_filters(original_query)
        parsed_queries = self.flatten(self.parse_add_word(query))

        log.info(f'Query: {parsed_queries} Filter: {filters}')

        to_scrape = []
        seen_urls = list()
        for query in parsed_queries:
            query_id, last_update = await self.db.insert_query(query)

            log.debug(f'Query ID: {query_id}')

            to_scrape.append((query_id, query))
            if last_update:
                # the query is exists
                # retrieve the offers from db
                all_offers = await self.db.retrieve_offers_from(query_id)

                length = len(all_offers)
                log.info(f'Offers in database: {length}')

                if all_offers:
                    for offer in all_offers:
                        # fill the seen_url lists
                        seen_urls.append(offer.url)
                        offer = self.filter(offer, filters)
                        if offer:
                            yield offer
        
        async for (id_, offer) in self.scrape(to_scrape, location, seen_urls):

            log.debug(f'Offer {offer.title} from QueryID {id_} Scraped')

            offer = self.filter(offer, filters)
            if offer:
                yield offer
                # saving offer in db 
                try:
                    await self.db.insert_entry(id_, offer)
                except Exception as e:
                    log.error(e)


    async def scrape(self, queries, location='London', seen_urls=[]):
        """ Run the scraper for each query in queries
        and analyses the offers"""
        log.info("Scraping started")
        log.debug(f'Queries : {queries}')

        # create coroutines for each queries
        coros = [self.api(id, query=q, location=location, seen=seen_urls).run() for (id, q) in queries]

        # merge these async generators into a single stream
        async for res in aiostream.stream.merge(*coros):
            query_id, offer = res

            log.debug(f'Got results from scraping query {query_id}, {offer.title}')

            if offer:
                # analyse the offer
                analysed = self.nlp.analyse(offer)
                yield query_id, analysed

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

    def filter(self, offer, filters):
        """ Filtering offers """
        if offer:
            if filters:
                found = 0
                for w in filters:
                    title = offer.title
                    title = title.lower()
                    if w in title:
                        found += 1
                if not found:
                    return offer
            else:
                return offer

    def flatten(self, x):
        """ Flatten a list of nested list of unknown depth to a simple list """
        if isinstance(x, collections.abc.Iterable) and not isinstance(x, str):
            return [a for i in x for a in self.flatten(i)]
        else:
            return [x]


if __name__ == '__main__':
    app = asyncio.run(App())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app.run()