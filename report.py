#!/usr/bin/env python3

import asyncio, aiosqlite
from collections import Counter, OrderedDict

import database, models
import numpy, matplotlib.pyplot
from wordcloud import WordCloud


class SkillsReport(models.aioObject):
    """ Analysing skills from the salem db in  /data/query-offer.db """

    async def __init__(self, db):
        self.db = db
        self.queries = await self.db.retrieve_all_queries()
        # trying to remove margins for all plots 
        matplotlib.rcParams['savefig.pad_inches'] = 0

    async def report_all(self):
        ct = await self.extract_skills()
        self.plot_bar_chart(ct)

    async def extract_skills(self):
        """ Extract skills from all queries 
        ::return:: Counter()"""
        queries = await self.db.retrieve_all_queries()
        ct = Counter() 
        in_ct = 0
        for qid, qname, _, __ in queries:
            try:
                offers = await self.db.retrieve_offers_from(qid)
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
        """ Plotting bar chart from skills counter object """
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
        """ Plotting word cloud from skills counter """
        wordcloud = WordCloud()
        wordcloud.generate_from_frequencies(frequencies=counter)
        
        matplotlib.pyplot.figure()
        matplotlib.pyplot.imshow(wordcloud, interpolation="bilinear")
        matplotlib.pyplot.axis("off")
        matplotlib.pyplot.show()
        

if __name__ == "__main__":
    data_type = models
    db_name = 'query-offer.db'

    async def test():
        db = await database.AsyncDB(db_name, data_type)
        report = await SkillsReport(db)
        await report.report_all()
        

    asyncio.run(test())      