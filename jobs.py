#!/usr/bin/env python3

import collections, asyncio, time, logging

import aiostream, urllib, http_

log = logging.getLogger(__file__)

class Offer(collections.namedtuple('JobOffer',  'title company salary location \
                                    type_ date txt url link skills matched',
                                    defaults=(0,))):
    def __eq__(self, other):
        """ Job offers are equal if the title and company of the offers are the same """
        if self.title.lower() == other.title.lower() and self.company.lower() == other.company.lower():
            return True
        else:
            return False


class Interface:
    """ There is a name for this type of class, need to google it.
    Essentialy is an interface to multiple objects with the same interface
    """
    def __init__(self, query, location='London', depth=3):
        # unpacking args
        self.query, self.location, self.depth = query, location, depth

        self.indeed = Indeed
        self.reed = Reed
    
    async def run(self):
        coros = [ self.indeed(self.query, self.location, self.depth).run(), 
                  self.reed(self.query, self.location).run()
                ]

        async for offer in aiostream.stream.merge(*coros):
            yield offer


class Indeed:
    """ Indeed.co.uk scraper """

    import lxml.html as data_parser

    BASE_URL = "http://www.indeed.co.uk"

    def __init__(self, query, location='London', depth=1, fromage=14):
        self.driver = http_

        self.seen_url = []
        self.depth = depth      
        self.query = query  

        self.params = {
            'q': query,
            'l': location,
            'sort': "date",
            'start': 0,
            'fromage': fromage      # only results under 2, 7, 14 days 
        }

    async def run(self):

        # create worker coroutines for each listing pages
        coros = [self._worker(url) for url in self.generate_listing_url()]
        
        # merge these async generators into a single stream
        async for offer in aiostream.stream.merge(*coros):
            yield offer

        # cleaning up on complete for next queries
        self.params['q'] = ''

    async def _worker(self, listing_url):
        """
        Define the work to be done for each listing to extract offers
        ::async yield:: JobOffer
        """
        log.debug(f'Working on: {listing_url}')

        async with self.driver.session_() as session:
            # note that the parent url is still unused 
            listing_body, listing_url = await self.driver.fetch(listing_url, session)

            # parse listing and request offers
            async for offer_body, offer_url in self.driver.fetch_all(self.parse_listing(listing_body), session):
                # parse offers
                for offer in self.parse_offer(offer_url, offer_body):
                    if offer:
                        yield offer

    def generate_listing_url(self):
        """
        Generating the listing urls by incrementing self.params['start']
        ::yield:: listing url
        """
        # generate listing urls
        for _ in range(self.depth):
            yield self.BASE_URL + "/jobs/?" + urllib.parse.urlencode(self.params)
            self.params['start'] += 10
        self.params['start'] = 0

    def parse_listing(self, html):
        """
        Parse listing pages
        ::yield:: offer url
        """
        # TODO : extract the job id or create a hash from title+company
        # and compare that to the database before fetching the page.

        root = self.data_parser.fromstring(html)

        # select all <a>
        all_a = root.xpath('//a[contains(@class, "jobtitle")]')

        found = len(all_a)
        log.info(f'{self.query} Found {found} on Indeed.co.uk')

        for a in all_a:
            offer_href = a.attrib['href']

            # skipping seen offers
            if offer_href not in self.seen_url:
                self.seen_url.append(offer_href)
                offer_url = self.BASE_URL + offer_href
                yield offer_url

    def parse_offer(self, body, url):
        """
        Parse offers page, 
        ::yield::: Offer
        """
        # TODO :
        # Better parsing for company name

        # performance bottleneck
        root = self.data_parser.fromstring(body)

        # extracting offer description
        description = root.xpath('//div[@id="jobDescriptionText"]')
        description = ' '.join(node.text_content() for node in description) or None

        # extracting the job title
        title = root.xpath('//h3')
        title = ' '.join(node.text_content() for node in title) or None

        # TODO : it's catching the number of reviews as well   
        # extracting company name 
        company = root.xpath('//div[contains(@class, "icl-u-lg-mr--sm")]')
        company = ' '.join(node.text_content() for node in company) or None

        # extracting salary
        salary = root.xpath('//div[contains(@class, "icl-IconFunctional--salary")]/parent::*')
        salary = ' '.join(node.text_content() for node in salary) or None
        if salary is None:
            # TODO: try to extract the salary from the description
            return ['0']
        # delete '-', '£' and ','
        salary = salary.replace('-', '').replace('£', '').replace(',', '')
        # google : (253 working days or 2080 hours per year)
        for word, multiplier in {'year': 1, 'month': 12, 'week': 52, 'day': 253, 'hour': 2080}.items():
            if word in salary:
                # getting rid of the text 
                salary = salary.replace(word, '').replace('a', '').replace('n', '')
                for value in salary.split():
                    # calculating yearly wage 
                    new_value = str(int(float(value) * multiplier))
                    salary = salary.replace(value, new_value)
        try:
            salary = salary.split()
        except:
            pass

        # extracting location
        location = root.xpath('//div[contains(@class, "icl-IconFunctional--location")]/parent::*')
        location = ' '.join(node.text_content() for node in location) or None

        # extracting job type
        type_ = root.xpath('//div[contains(@class, "icl-IconFunctional--jobs")]/parent::*')
        type_ = ' '.join(node.text_content() for node in type_) or None

        # extracting relative date
        date = root.xpath('//div[contains(@class, "jobsearch-JobMetadataFooter")]')
        if date:
            date = ' '.join(node.text_content() for node in date).lower()
            # if it was posted today
            if "today" in date or "just posted" in date:
                date = 0
            else: # i.e: 26 days ago
                for n in date.split(" "):
                    if n.isdigit():
                        date = n

        apply_link = root.xpath('//a[contains(@class, "icl-Button")]')
        if apply_link:
            apply_link = apply_link[0].attrib['href']
            # for apply with indeed, the href is generated by javascript
            # TODO : work this out
            if apply_link == '/promo/resume':
                apply_link = url
    
        new_offer = Offer(title, company, salary, location, type_, date, description, url, url, 'N/A')
        
        # further parsing and analysing 
        yield new_offer


class Reed:
    """ Api wraper for Reed.co.uk"""

    import json as data_parser

    API_KEY = "51db9ad0-f9cd-4041-b4e1-7bc88b023491"
    version = 1.0
    BASE_URL = f'http://www.reed.co.uk/api/{version}'

    def __init__(self, query, location='London'):
        self.query = query

        self.driver = http_

        self.params = {
            'keywords' : query,
            'location' : location
        }

    async def run(self):
        query_url = self.BASE_URL + '/search?' + urllib.parse.urlencode(self.params)

        # define auth
        api_auth = self.driver.aiohttp.BasicAuth(login=self.API_KEY)

        # pass the auth to the http session
        async with self.driver.session_(auth=api_auth) as session:
            # listing body is json string
            listing_body = await self.driver.fetch(query_url, session)
            async for offer_body, offer_url in self.driver.fetch_all(self.parse_listing(listing_body), session):
                for offer in self.parse_offer(offer_body, offer_url):
                    if offer:
                        yield offer

    def parse_listing(self, data):
        json_, url = data
        json_ = self.data_parser.loads(json_)
        results = json_['results']

        found = len(results)
        log.info(f'{self.query} - Found {found} on Reed.co.uk')

        for offer in results:
            offer_url = self.BASE_URL + '/jobs/' + str(offer['jobId'])
            yield offer_url

    def parse_offer(self, body, url):
        json_ = self.data_parser.loads(body)
            
        new_offer = Offer(json_['jobTitle'], json_['employerName'], [json_['yearlyMinimumSalary'], json_['yearlyMaximumSalary']], 
                          json_['locationName'], json_['fullTime'], json_['datePosted'], json_['jobDescription'], 
                          json_['jobUrl'], json_['jobUrl'], 'N/A')
        yield new_offer


if __name__ == "__main__":
    import sys 

    try:
        query = sys.argv[1]
    except IndexError:
        print("Please provide query string in argument")
        exit(1)

    # TODO: move all of these to a /test
    async def test_indeed():
        indeed = Indeed(query)
        async for offer in indeed.run():
            print(offer.title, offer.company, offer.salary)

    async def test_reed():
        reed = Reed(query)
        async for offer in reed.run():
            print(offer.title, offer.txt)

    loop=asyncio.get_event_loop()
    loop.run_until_complete(test_reed())
    loop.close()