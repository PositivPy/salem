#!/usr/bin/env python3

import collections, asyncio, time

import aiostream, lxml.html, urllib


class Offer(collections.namedtuple('JobOffer',  'title company salary location \
                                    type_ date txt url link skills',
                                    defaults=(0,))):
    def __eq__(self, other):
        """ Job offers are equal if the title and company of the offers are the same """
        if self.title.lower() == other.title.lower() and self.company.lower() == other.company.lower():
            return True
        else:
            return False

class Indeed:
    """ Indeed scraper class """

    BASE_URL = "https://www.indeed.co.uk"

    import http_ as driver
    from nltk_ import IndeedNLTK 
    # TODO : make it async and move it to controler ?
    nltk_ = IndeedNLTK()

    def __init__(self, fromage=14):

        self.seen_url = []
        
        self.params = {
            'q': '',
            'l': '',
            'sort': "date",
            'start': 0,
            'fromage': fromage      # only results under 2, 7, 14 days 
        }

    async def get(self, query, depth=1, location='London'):
        self.params['q'] = query
        self.params['l'] = location

        # create worker coroutines for each listing pages
        coros = [self._worker(url) for url in self.generate_listing_url(pages=depth)]
        
        # merge these async generators into a single stream
        async for offer in aiostream.stream.merge(*coros):
            yield offer

        # cleaning up on complete for next queries
        self.params['q'] = ''

    async def _worker(self, url):
        """
        Define the work to be done for each listing to extract offers
        ::async yield:: JobOffer
        """
        async with self.driver.session_() as session:
            # note that the parent url is still unused 
            listing_body, url = await self.driver.fetch(url, session)

            # TODO: parse offers in coroutines and yield as_completed()
            # parse listing and request offers
            async for offer_body, offer_url in self.driver.fetch_all(self.parse_listing(listing_body), session):
                # parse offers
                for offer in self.parse_offer(offer_url, offer_body):
                    if offer:
                        yield offer

    def generate_listing_url(self, pages=1):
        """
        Generating the listing urls by incrementing self.params['start']
        ::yield:: listing url
        """
        # generate listing urls
        for _ in range(pages):
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

        root = lxml.html.fromstring(html)

        # select all <a>
        all_a = root.xpath('//a[contains(@class, "jobtitle")]')
        for a in all_a:
            offer_href = a.attrib['href']

            # skipping seen offers
            if offer_href not in self.seen_url:
                self.seen_url.append(offer_href)
                offer_url = self.BASE_URL + offer_href
                yield offer_url

    def parse_offer(self, url, html):
        """
        Parse offers page, 
        ::yield::: Offer
        """
        # TODO :
        # Better parsing for company name

        # performance bottleneck
        root = lxml.html.fromstring(html)

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

        """
        # TODO :
        # extracting the apply link
        button_div = root.xpath('//div[@id="indeedApplyButtonContainer"]/child::span')
        try:
            span = lxml.html.tostring(button_div[0])
            # job id, company name and job title is in span
            try:
                
                print(span)
                print("WORKED")
            except:
                print("URL")
        except:
            if button_div:
                print("FUCKED")
                print(lxml.html.tostring(button_div[0]))
            else:
                print("MEGA FUCKED")
        """
        apply_link = root.xpath('//a[contains(@class, "icl-Button")]')
        if apply_link:
            apply_link = apply_link[0].attrib['href']
            # for apply with indeed, the href is generated by javascript
            # TODO : work this out
            if apply_link == '/promo/resume':
                apply_link = url
    
        new_offer = Offer(title, company, salary, location, type_, date, description, url, apply_link)
        
        # further parsing and analysing 
        yield self.nltk_.analyse(new_offer)


if __name__ == "__main__":
    import sys 

    try:
        query = sys.argv[1]
    except IndexError:
        print("Please provide query string in argument")
        exit(1)

    # example function on how to use the scraper
    async def test():
        depth = 5
        indeed = Indeed(depth)

        async for offer in indeed.query(query):
            print(offer.title, offer.company, offer.salary)

    # run the test
    loop=asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()
    # Or:
    #asyncio.run(main())
