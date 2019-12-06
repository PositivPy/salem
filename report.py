#!/usr/bin/env python3

""" This script is meant for analysing the database /data/query-offer.db """

import asyncio
from collections import Counter, OrderedDict
import model
import database, nlp
import aiosqlite
from aiosqlite import IntegrityError
import statistics
import matplotlib.pyplot as plt 
import numpy as np 
import json
from wordcloud import WordCloud


class ManagedDB(database.AsyncDB):

    async def __init__(self, name, data_type):
        self.name, self.data_type = name, data_type
        await super().__init__(self.name, self.data_type)

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

async def plot_salary_stats(db):
     
    
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

async def skills_extraction(db):

    queries = await db.retrieve_all_queries()
    ct = Counter() 
    in_ct = 0
    for qid, qname, _, __ in queries:
        try:
            offers = await db.retrieve_offers_from(qid)
            for offer in offers:
                in_ct += 1

                skills = offer[7]
                skills = skills.replace('[', '')
                skills = skills.replace("'", '')
                skills = skills.replace(']', '')
                skills = skills.split(', ')
                for skill in skills:
                    ct[skill] += 1
        except :
            "Nothing found" 
        

    # sort counter 
    ct = OrderedDict(ct.most_common())
    print(f'Total Offers: {in_ct}')
    return ct

def plot_bar_chart(counter):
    if not counter:
        return
    print(counter)
    labels, values = zip(*counter.items())
    indexes = np.arange(len(labels))
    width = 1

    plt.bar(indexes, values, width)
    
    # hidding skills labels
    #frame1 = plt.gca()
    #frame1.axes.xaxis.set_ticklabels([])
    plt.xticks(indexes + width * 0.5, labels, rotation=90)

    # adjusting the frame
    plt.subplots_adjust(left=0.10, bottom=0.08, right=0.97, top=0.94)

    plt.xlabel('Skills') 
    plt.ylabel('Frequency')
    # giving a title to my graph 
    plt.title('Skills Frequency') 
    

    plt.show()

def plot_word_cloud(counter):
    wordcloud = WordCloud()
    wordcloud.generate_from_frequencies(frequencies=counter)
    
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()
        

if __name__ == "__main__":
    import sys

    async def test():
        data_type = model
        name = 'query-offer.db'
        db = await ManagedDB(name, data_type)
    # define async test function 
        ct = await skills_extraction(db)
        plot_bar_chart(ct)
        #asyncio.run(plot_salary_stats(name))  
    asyncio.run(test())      