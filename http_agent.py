#!/usr/bin/env python3

import requests


DEFAULT_ENCODING = 'windows-1252'
TEST = None

class Response:

    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

    def __repr__(self):
        return '<Response status_code="{status}" lenght="{lenght}">'.format(
            lenght=len(self.content), status=self.status_code)


class RequestsHTTP:

    def __init__(self):
        self.driver = requests.Session()
        if TEST and self.driver :
            print("Driver initialised properly")

    def get(self, url, parameters=None):
        if TEST:
            print("Trying to connect to", url)
        try:
            response = self.driver.get(url, params=parameters)
            return Response(
                response.status_code, response.content.decode(
                    DEFAULT_ENCODING))
        except Exception as e:
            if TEST:
                print(e)
            raise Exception

if __name__=="__main__":
    TEST = True 

    print("Starting test")
    agent = RequestsHTTP()
    res = agent.get("http://www.google.com")
    if res.status_code == 200:
        print("Test successful.")
    else:
        print("Test unsuccessful, please check internet connection.")
