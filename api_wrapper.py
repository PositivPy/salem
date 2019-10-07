#!/usr/bin/env python3

from bs4 import BeautifulSoup as bs
import http_agent


class API_results:

    def __init__(self, content={}):
        self.content = content

    def __repr__(self):
        print(self.content)

    def append(self, content):
        self.content.append(content)


class API_wrapper:
    """ Define the basic scraper class """

    URL = None
    API_KEY = None

    def __init__(self, params):
        self.params = params

    def get_listing(self):
        raise NotImplemented

    def get_single_ad(self, url):
        raise NotImplemented


class Indeed(API_wrapper):
    import json 

    # should import from config file 
    URL = "Indeed URL"
    API_KEY = "" "Also know as the publisher key on indeed"
    version = "2"
    # should be built before ?
    user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) \
            Gecko/20100101 Firefox/47.0"
    limit = 25

    def __init__(self, query, location='London'):
        self.res = API_results()
        self.params = {
            'publisher': self.API_KEY,
            'q': query,
            'l': location,
            'sort': "date",
            'format': "json",
            'v': self.version,
            'useragent': self.user_agent,
            'start' : "0"
        }

    def get_listing(self):
        driver = http_agent.RequestsHTTP()
        try:
            response = driver.get(self.URL, self.params)
            self.res = API_result.append(response.content.json())         
        except Exception as e:    
                print("Error getting listing! {}".format(e)) 
        if self.limit < res.content["totalResults"]:
            start = int(self.params["start"])
            if start < int(res.content["totalResults"]):
                self.params["start"] = str(start + self.limit)
            return self.get_listing()
        return self.res

    def get_single_ad(self, url):
        raise NotImplemented

if __name__ == "__main__":
    indeed = Indeed("je ne sais pas")
