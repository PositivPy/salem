import asyncio, collections

import database, model

import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np

import sys
# enable traceback for debugging
sys.tracebacklimit=1

# TODO : move aioObject somewhere else
class aioObject(object):
    """ Inheriting this class allows you to define an async __init__.
    So you can create objects by doing something like 'await MyClass(params)'
    https://stackoverflow.com/questions/33128325/how-to-set-class-attribute-with-await-in-init
    """
    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self):
        pass


class PlotSalaries(aioObject):
    """ Ploting salary stats for all queries in '/data/<db_name>.db' """
    async def __init__(self, db_name):
        self.db = await database.AsyncDB(db_name, model)
        self.queries = await self.db.retrieve_all_queries()
    
    async def calculate_salary_freq(self, query_id):
        offers = await self.db.retrieve_offers_from(query_id)
        if offers:
            df = pd.DataFrame(data=offers)
            # set numeric type if possible
            df = df.apply(pd.to_numeric, errors='ignore')

            # remove ads with no advertised salaries
            df = df[df.minSalary != 0]
            # just in case; if maxSalary = 0 ; maxSalary = minSalary
            df['maxSalary'] = df['maxSalary'].apply(lambda x: df['minSalary'] if x == 0 else x)

            # min and max are actual mini/maxi
            min_ = df['minSalary'].min()
            max_ = df['maxSalary'].max()

            '''
            From Reddit:
            You can convert each salary range to a uniform distribution over that range
            (so the "height" will be 1/width), add together these distributions,
            divide by the number of samples to normalize the sum.

            A simplified version of the above if you simply subdivide the possible salaries
            to a fixed resolution first, like $1000 ranges. Then if you have a data point 
            of between 10k and 15k, you can simply replace it by 5 data points: 
            between 10k and 11k, between 11k and 12k, etc... But each with 1/5 weight. 
            '''

            # width of a box in £
            box_width = 5000
            # query_width: number of boxes until max is reached 
            query_width = int(max_ // box_width) + 1
            
            # create a list of indexes 
            indexes = [box * box_width for box in range(query_width)]
            
            res = collections.defaultdict(int)
            for i, row in df.iterrows():
                boxes_filled = []
                for index in indexes:
                    if row['minSalary'] < index and row['maxSalary'] >= index:
                        #print(row['minSalary'], '<', index, '<', row['maxSalary'])
                        boxes_filled.append(index)
                # weigth of the offer in each boxes
                if boxes_filled:
                    weigth = 1 / len(boxes_filled)
                    for box in boxes_filled:
                        res[box] += weigth         
            # sorting res by key
            sort = collections.OrderedDict(sorted(res.items()))

            ax = plt.axes()
            #ax.set_xticklabels(sort.keys())

            ax.bar(sort.keys(), sort.values(), box_width, color='blue')
            plt.show()
            

    async def real_plot(self):
        for qid, qname, _, qcount in self.queries:
            try:
                await self.calculate_salary_freq(qid)
            except:
                pass 
        #plt.show()

    async def calculate_salary_stats(self, query_id):
        offers = await self.db.retrieve_offers_from(query_id)
        if offers:
            df = pd.DataFrame(data=offers)
            # set numeric type if possible
            df = df.apply(pd.to_numeric, errors='ignore')

            # remove ads with no advertised salaries
            df = df[df.minSalary != 0]
            # just in case if maxSalary = 0 ; maxSalary = minSalary
            df['maxSalary'] = df['maxSalary'].apply(lambda x: df['minSalary'] if x == 0 else x)

            # select only salary min and max column
            col = df.loc[: , "minSalary":"maxSalary"]
            # calculating the mean of each column 
            df['salary_mean'] = col.mean(axis=1).astype(int) 

            # using the offers' mean to calculate query's mean and median
            offers_mean = df.salary_mean

            mean = int(offers_mean.mean())
            median = int(offers_mean.median())

            # min and max are actual mini/maxi
            min_ = df['minSalary'].min()
            max_ = df['maxSalary'].max()

            return mean, median, min_, max_


    async def plot_salary_stats(self):
        """ Plots the salary stats of all queries into a figure """

        stats = []
        for qid, qname, _, qcount in self.queries:
            try:
                stat = await self.calculate_salary_stats(qid)
                # skipping queries with no offers, thus no stats
                if stat:
                    stats.append((qid, qname, stat))
            except:
                # BUG: probably offer sanitisation problem
                # returning exception near ")": syntax error
                pass 
        # sort stats by max
        stats.sort(key=lambda item: item[2][3])
        
        # ie. stats = [(qid, query_name,( avg, median, max, min )) * n_queries]
        # separating data into numpy arrays
        labels = np.array([item[1] for item in stats])
        average = np.array([item[2][0] for item in stats])
        median = np.array([item[2][1] for item in stats])
        max_ = np.array([item[2][3] for item in stats])
        min_ = np.array([item[2][2] for item in stats])

        # creating a new subplot 
        fig, axs = plt.subplots()

        # plotting lines 
        axs.plot(average, labels, label = "Mean") 
        axs.plot(median, labels, label = "Median") 
        axs.plot(min_, labels, label = "Min") 
        axs.plot(max_, labels, label = "Max") 

        # filling between lines
        axs.fill_betweenx(labels, average, max_, color='red')
        axs.fill_betweenx(labels, average, median, color='yellow')
        axs.fill_betweenx(labels, median, min_, color='green')

        # ploting the living wage
        axs.axvline(x=22360, color='k', linestyle=':', label="Living Wage")

        plt.show()

if __name__ == "__main__":
    async def test():
        analyser = await PlotSalaries('query-offer.db')
        await analyser.calculate_salary_freq(1  )

    asyncio.run(test())