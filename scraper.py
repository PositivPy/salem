#!/usr/bin/env python3

from bs4 import BeautifulSoup as bs
import collections   # Don't forget nammedTuples
import urllib
import asyncio
import aiostream
import time

Offer = collections.namedtuple('JobOffer', 'title company salary location \
                                            type_ date txt url link skills',
                                            defaults=(0,))

class Indeed:

    BASE_URL = "https://www.indeed.co.uk"

    import http_ as driver
    from nltk_ import IndeedNLTK
    nltk_ = IndeedNLTK()

    def __init__(self, depth=1, location='London', fromage=14):

        self.depth = depth

        self.params = {
            'q': '',
            'l': location,
            'sort': "date",
            'start': 0,
            'fromage': fromage      # only results under 2, 7, 14 days
        }

        self.seen_url = []

        # for stats
        self.skipped = int()
        self.start = int()
        self.end = int()


    async def query(self, query):
        self.start = time.time()

        #print(f'Scraping {depth} pages for [ {query} ]')
        self.params['q'] = query
        # create worker coroutines for each listing pages
        coros = [self._worker(url) for url in self.generate_listing_url(pages=self.depth)]
        # merge async generators into a single stream
        async for item in aiostream.stream.merge(*coros):
                yield item

        # cleaning up on complete for next queries
        self.params['q'] = ''

        # I like stats
        self.end = time.time()

    async def _worker(self, listing_url):
        """
        Define the worker coroutine, core of the scraper
        ::yield:: JobOffer
        """
        # note that the parent url is still unused
        listing_body, url = await self.driver.fetch_single(listing_url)

        # parse listing and request offers
        async for offer_body, offer_url in self.driver.fetch_all(self.parse_listing(listing_body)):
            # parse offers
            for offer in self.parse_offer(offer_body, offer_url):
                if offer is not None:
                    yield offer

    def generate_listing_url(self, pages):
        """
        Generates the listing urls by incrementing the start parameter
        ::yield:: listing urls
        """
        # generate listing urls
        for i in range(pages):
            yield self.BASE_URL + "/jobs/?" + urllib.parse.urlencode(self.params)
            self.params['start'] += 10
        self.params['start'] = 0

    def parse_listing(self, html):
        """
        Parse listing pages, extracting offer href
        ::yield:: urls
        """
        soup = bs(html, features="lxml")

        # extracting job titles containing the offer's href
        for a in soup.find_all("a", class_="jobtitle"):
            offer_url = a['href']

            # check if url has already been scraped
            if offer_url not in self.seen_url:
                # keeping track of scraped urls
                self.seen_url.append(offer_url)
                # href is added to the base url
                yield self.BASE_URL + offer_url
            # skipping seen offers
            else:
                self.skipped += 1

    def parse_offer(self, html, url):
        """
        Parse offers page, nltk is used at the end to extract and sanitise
        fields that could't be extracted with beautifulsoup.
        ::yield::: Offer
        """
        soup = bs(html, features="lxml")

        # extracting offer description
        corpus = corpus = soup.find("div", class_="jobsearch-jobDescriptionText")
        if corpus:
            corpus = corpus.text

        # extracting the job title
        title = soup.find("h3")
        if title:
            title = title.text

        # extracting company name
        company = soup.find("div", class_="icl-u-lg-mr--sm")
        if company:
            company = company.text

        # extracting salary
        salary = soup.find("div", class_="icl-IconFunctional--salary")
        if salary:
            salary = salary.parent.find("span", class_="jobsearch-JobMetadataHeader-iconLabel").text

        # extracting location
        location = soup.find("div", class_="icl-IconFunctional--location")
        if location:
            location = location.parent.find("span", class_="jobsearch-JobMetadataHeader-iconLabel").text

        # extracting job type
        type_ = soup.find("div", class_="icl-IconFunctional--jobs")
        if type_:
            type_ = type_.parent.find("span", class_="jobsearch-JobMetadataHeader-iconLabel").text

        # extracting relative date
        date = soup.find("div", class_="jobsearch-JobMetadataFooter")
        if date:
            date = date.text.lower()
            # if it was posted today
            if "today" in date or "just posted" in date:
                date = 0
            else: # i.e: 26 days ago
                for n in date.split(" "):
                    if n.isdigit():
                        date = n

        # extracting the apply link
        apply_link = soup.find('a', class_="icl-Button")
        if apply_link:
            apply_link = apply_link['href']
            # for apply with indeed, the href is generated by javascript
            # TODO : work this out
            if apply_link == '/promo/resume':
                apply_link = url

        new_offer = Offer(title, company, salary, location, type_, date, corpus, url, apply_link)

        yield new_offer
        # further parsing and analysing
        #yield self.nltk_.analyse(new_offer)

    def stats(self):
        nb_expected = self.depth * 19    # 19 ads per listings
        nb_fetch = len(self.seen_url)
        total_time = self.end - self.start
        return f'Finished crawling {self.depth} listing in {total_time}\
                \nExpected: {nb_expected} Got: {nb_fetch} Skipped: {self.skipped}'


if __name__ == "__main__":
    import sys

    query = sys.argv[1]

    async def main():

        depth = 2

        indeed = Indeed(depth)
        expected = depth * 19

        offers = []
        async for offer in indeed.query(query):
            print(offer)

            #offers.append(offer)
        """
        for offer in offers:
            if offer is None or offer.salary is None:
                offers.remove(offer)

        soffers = sorted(offers, key=lambda x: x.salary[0] if x.salary[0] else x.salary, reverse=True)

        for offer in soffers:
            title, company, salary, location, type_, date, txt, url, link, skills = offer
            if salary == '0':
                continue
            if int(salary[len(salary)-1]) < 21944:
                continue
            print(f'\n{title}\nCompany: {company}\nType: {type_}\nSalary: {salary}')
            print(f'Skills: {skills}')
        print(indeed.stats())
    """
    loop=asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
    #asyncio.run(main())
