#!/usr/bin/env python3

import argparse 
import sys
import model, api

# the controller will build the model, search module into an object 
# this object will be responsible for updating everyone
# when listing comes update database 
# when database updated 

# check the hash of the query in db to know if first time crawl

class Controller:
    
    def __init__(self, args, model, api)
        self.args = args
        self.db = model.DataBase(args.type)  # Different databases for job and item
        self.api = self.get_api()            # Possible to have multiple api
        
    def search(self):
        res = self.api.get_listing()
        self.model.append(res)
        print(self.model.search(args)


def main(args):
    if args.type == "job":
        print(args.query)
    if args.type == "item":
        print("Not yet implemented")
    print(args.location)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("type", help = "What are you searching for ? job or item")
    parser.add_argument("query", help = "Your search string within quotes")
    parser.add_argument("-l", "--location", default = "London", 
                        help = "Define the location of your search. User postal \
                        code or a city, state, province.")
    try :
        args = parser.parse_args()
        main(args)
    except:
        parser.print_help()
