#!/usr/bin/env python3

from bs4 import BeautifulSoup as bs
import collections
import urllib
import asyncio

class Offer(object):

    def __init__(self, id, title, href):
        self.id = id 
        self.title = title
        self.link = href
        self.salary = None
        self.company = None
        self.location = None
        
    def __str__(self):
        return "Title : {title}, Salary : {salary}, Company : {company}".format(
            title=self.title, salary=self.salary, company=self.company)


class IndeedScraper:

    import _http as driver

    BASE_URL = "https://www.indeed.co.uk"

    def __init__(self, query, callback, location='London', fromage=14):
        self.callback = callback
        self.params = {
            'q': query,
            'l': location,
            'sort': "date",
            'start': 0,
            'fromage':fromage # only results under 7, 14 days 
        }

    async def run(self):
        coro = [self.get_offer_from(i) for i in self._crawl_listing()]
        for first_completed in asyncio.as_completed(coro):
            await first_completed

    # listing url generator
    def _crawl_listing(self):
        for i in range(10):
            yield self.BASE_URL + "/jobs/?" + urllib.parse.urlencode(self.params)
            self.params['start']

    async def get_offer_from(self, url):
        # pass the url generator to the http driver
        body = await self.driver.fetch_single(url)
        async for offers in self.driver.fetch_all(self.parse_listing(body)):
            self.parse_offer(offers)

    def parse_listing(self, html):
        """ 
        Parse listing pages, yield offer urls.
        """
        soup = bs(html, features="lxml")
        divs = soup.findAll("div", class_="result")
        if len(divs) > 0:
            for div in divs:
                _id = div['id']
                for a in div.find_all("a", class_="jobtitle"):
                    yield self.BASE_URL + a['href']

    def parse_offer(self, html):
        """
        Parse offers page, yield Offer object.
        """
        soup = bs(html, features="lxml")

        # extracting offer description
        corpus = "".join([" " + p.text for p in soup.findAll("p")],)
        
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

        print(f'{title} for {company} in {location}\n{type_} for {salary}')
    
        print("###############")


if __name__ == "__main__":
    indeed = IndeedScraper("python", print)
    asyncio.run(indeed.run())
    #asyncio.run(indeed.request_listing())
