#!/usr/bin/env python3

""" This script is meant for analysing the database /data/query-offer.db """

import asyncio, aiosqlite
from collections import Counter, OrderedDict

import database, model
import numpy, matplotlib.pyplot
from wordcloud import WordCloud


class SkillsReport(object):
    """ Analysing skills from the salem db """

    async def report_all(self):
        data_type = model
        name = 'query-offer.db'
        db = await database.AsyncDB(name, data_type)
        ct = await self.extract_all(db)
        self.plot_bar_chart(ct)

    async def extract_all(self, db):
        """ Extract skills from all queries 
        ::return:: Counter()"""
        queries = await db.retrieve_all_queries()
        ct = Counter() 
        in_ct = 0
        for qid, qname, _, __ in queries:
            try:
                offers = await db.retrieve_offers_from(qid)
                for offer in offers:
                    in_ct += 1

                    skills = offer[7]
                    # parsing skills string to list 
                    skills = skills.replace('[', '')
                    skills = skills.replace("'", '')
                    skills = skills.replace(']', '')
                    skills = skills.split(', ')

                    # adding the skills to the counter
                    for skill in skills:
                        ct[skill] += 1
            except :
                "Nothing found" 
        # sort counter 
        ct = OrderedDict(ct.most_common())
        print(f'Total Offers: {in_ct}')
        return ct

    def plot_bar_chart(self, counter):
        if not counter:
            return
        labels, values = zip(*counter.items())
        indexes = numpy.arange(len(labels))
        width = 1

        matplotlib.pyplot.bar(indexes, values, width)
        
        # hidding skills labels
        #frame1 = matplotlib.pyplot.gca()
        #frame1.axes.xaxis.set_ticklabels([])
        matplotlib.pyplot.xticks(indexes + width * 0.5, labels, rotation=90)

        # adjusting the frame
        matplotlib.pyplot.subplots_adjust(left=0.10, bottom=0.08, right=0.97, top=0.94)

        matplotlib.pyplot.xlabel('Skills') 
        matplotlib.pyplot.ylabel('Frequency')
        # giving a title to my graph 
        matplotlib.pyplot.title('Skills Frequency') 
        
        matplotlib.pyplot.show()

    def plot_word_cloud(self, counter):
        wordcloud = WordCloud()
        wordcloud.generate_from_frequencies(frequencies=counter)
        
        matplotlib.pyplot.figure()
        matplotlib.pyplot.imshow(wordcloud, interpolation="bilinear")
        matplotlib.pyplot.axis("off")
        matplotlib.pyplot.show()
        

if __name__ == "__main__":
    report = SkillsReport()

    asyncio.run(report.report_all())      