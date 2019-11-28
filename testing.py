""" This script is meant for analysing the database /data/query-offer.db """

import asyncio

import model
import aiosqlite
from aiosqlite import IntegrityError
import statistics
import matplotlib.pyplot as plt 
import numpy as np 

class ManagedDB(model.AsyncDB):

    async def __init__(self, name):
        self.name = name
        await super().__init__(self.name)

    def work(func):
        """ Async decorator: opening the database in a context manager before use """
        async def _wraper(*args):
            # decorator in class : extract self from function args
            self = args[0]
            # open connection in a context manager
            async with aiosqlite.connect(self.name) as self.con:
                self.cursor = await self.con.cursor()
                return await func(*args)
        return _wraper
        
    @work 
    async def retrieve_all_queries(self):
        await self.cursor.execute('''SELECT rowid, * from QUERIES ;''')
        return await self.cursor.fetchall()

    @work
    async def retrieve_all_offers(self):
        await self.cursor.execute('''SELECT rowid from OFFERS ;''')
        res = await self.cursor.fetchall()
        print(res)

    @work
    async def retrieve_all_relation(self):
        await self.cursor.execute('''SELECT * from QUERY_TO_OFFER''')
        res = await self.cursor.fetchall()
        print(res)


def median_mean_salary(offers):
    salaries = [int(offer[4]) for offer in offers if int(offer[4]) > 0]
    salaries.sort(reverse=True)
    print(salaries)
    
    avg = int(statistics.mean(salaries))
    median = int(statistics.median(salaries))
    min_ = int(min(salaries))
    max_ = int(max(salaries))

    print(f'Median: {median} Average: {avg} Min: {min_} Max: {max_}')
    return avg, median, min_, max_
    
def plot(stats):
        # ie. stats = [(query_name, avg, median)*n_queries]
        # separating data into numpy arrays
        labels = np.array([item[0] for item in stats])
        average = np.array([item[1] for item in stats])
        median = np.array([item[2] for item in stats])
        min_ = np.array([item[3] for item in stats])
        max_ = np.array([item[4] for item in stats])

        # plotting the line 1 points  
        plt.plot(labels, average, label = "Mean") 
        plt.plot(labels, median, label = "Median") 
        plt.plot(labels, min_, label = "Min") 
        plt.plot(labels, max_, label = "Max") 
 
        # ploting the living wage
        plt.axhline(y=22360, color='k', linestyle=':', label="Living Wage")

        # naming the y axis 
        plt.ylabel('Salary') 
        # giving a title to my graph 
        plt.title('Job to Salary') 
        
        # show a legend on the plot 
        plt.legend() 

        # rotating the labels
        plt.xticks(rotation=90)

        # filling between lines
        plt.fill_between(labels, average, max_, color='red')
        plt.fill_between(labels, average, median, color='yellow')
        plt.fill_between(labels, median, min_, color='green')

        plt.subplots_adjust(left=0.14, bottom=0.3, right=0.96, top=0.93)
        
        # function to show the plot 
        plt.show() 
    

if __name__ == "__main__":
    import sys

    name = 'query-offer.db'
    id_ = '2'

    # define async test function 
    async def test(name):
        db = await ManagedDB(name)

        stats = []
        print(stats)
        queries = await db.retrieve_all_queries()
        for qid, qname, _, qcount in queries:
            print(qid, qname)
            try:
                offers = await db.retrieve_offers(qid)
            except TypeError:
                "nothing found"
            try:
                avg, median, min_, max_ = median_mean_salary(offers)
                stats.append((qname, avg, median, min_, max_))
            except statistics.StatisticsError:
                print("nothing found")
            
        # sort stats by max
        stats.sort(key=lambda item: item[4])

        plot(stats)
    # run test function
    asyncio.run(test(name))        