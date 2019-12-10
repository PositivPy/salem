#!/usr/bin/env python3

import asyncio, aiosqlite
from collections import Counter, OrderedDict, defaultdict

import database, models
import pandas, numpy, matplotlib, matplotlib.pyplot, matplotlib.gridspec
from matplotlib.ticker import FuncFormatter
from wordcloud import WordCloud

# setting general styling 
#matplotlib.pyplot.style.use('ggplot')


class SalariesReport(models.aioObject):
    """ Ploting salary stats for all queries in '/data/<db_name>.db' """

    async def __init__(self, db):
        self.db = db
        self.queries = await self.db.retrieve_all_queries()
        # trying to remove margins for all plots 
        matplotlib.rcParams['savefig.pad_inches'] = 0
    
    async def report_all(self):
        # calculating stats for all queries
        total_offers = 0
        stats = []
        for qid, qname, _, qcount in self.queries:
            try:
                dataframe, mean, median, min_, max_ = await self.calculate_salary_stats(qid)
                stats.append((qname, dataframe, max_, min_, mean, median))
                total_offers += len(dataframe.index)
            except Exception:
                # the query is empty
                pass

        # sort stats by max and median for fallback (if two max are equal)
        stats.sort(key=lambda item: (item[2], item[5]), reverse=True)

        fig = matplotlib.pyplot.figure()

        main_gridspec = matplotlib.gridspec.GridSpec(1, 2, wspace=0.1)
        
        # creating the grid spec for the histograms 
        left_gridspec = matplotlib.gridspec.GridSpecFromSubplotSpec(len(stats), 1, main_gridspec[1])

        ## plotting curves
        curve_ax = fig.add_subplot(main_gridspec[0])
        await self.plot_curves(curve_ax, stats)

        ## undelay for the distribs' legends
        under_ax = fig.add_subplot(main_gridspec[1], sharex=curve_ax, sharey=curve_ax)
        under_ax.yaxis.set_visible(False)
        #under_ax.patch.set_visible(False)
        
        # plotting living wage
        under_ax.axvline(x=22360, color='k', linestyle=':', label="Living Wage")

        # re-sort the stats in reverse this time 
        stats.sort(key=lambda item: (item[2], item[5]))

        ## plotting distribs 
        count = 0
        while count < len(stats):
            ax = fig.add_subplot(left_gridspec[count, 0], sharex=curve_ax)
            self.plot_distrib(ax, stats[count], 1000)
            count += 1

        ## setting titles
        fig.suptitle('SALARY COMPARAISON REPORT\n Salary Data for London, UK', y=0.99, fontsize=14)
        curve_ax.set_title('Annual Average Wage')
        under_ax.set_title('Annual Wage Distribution')
        matplotlib.pyplot.text(0.45, 0.03, f"Total sample size: {total_offers} offers.", fontsize=8, transform=fig.transFigure)
        

        matplotlib.pyplot.show()

    async def calculate_salary_stats(self, query_id):
        offers = await self.db.retrieve_offers_from(query_id)
        if offers:
            df = pandas.DataFrame(data=offers)
            # set numeric type if possible
            df = df.apply(pandas.to_numeric, errors='ignore')

            # remove ads with no advertised salaries
            df = df[df.minSalary != 0]
            # just in case; if maxSalary = 0 ; maxSalary = minSalary
            df['maxSalary'] = df['maxSalary'].apply(lambda x: df['minSalary'] if x == 0 else x)

            ## calculating mean and median 
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

            return df, mean, median, min_, max_

    def plot_distrib(self, ax, stat, box_width=500):
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
        # unumpyacking stats
        qname, df, max_, min_, mean, median = stat

        # query_width: number of boxes until max is reached 
        query_width = int(max_ // box_width) + 1
        
        # create a list of indexes 
        indexes = [box * box_width for box in range(query_width)]
        
        res = defaultdict(int)
        for i, row in df.iterrows():
            boxes_filled = []
            for index in indexes:
                if index in range(row['minSalary'], row['maxSalary']):
                    boxes_filled.append(index)
            # weigth of the offer in each boxes
            if boxes_filled:
                weigth = 1 / len(boxes_filled)
                for box in boxes_filled:
                    res[box] += weigth         
        # sorting res by key
        sort = OrderedDict(sorted(res.items()))
            
        # plot the bar chart
        barplot = ax.bar(sort.keys(), sort.values(), box_width) 

        # removing all borders and ticks
        ax.yaxis.set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.xaxis.set_visible(False)
        ax.spines['bottom'].set_visible(False)

        # transparent background
        ax.patch.set_visible(False)

    async def plot_curves(self, ax, stats):
        # separating data into numpy arrays
        labels = numpy.array([item[0] for item in stats])

        average = numpy.array([item[4] for item in stats])
        median = numpy.array([item[5] for item in stats])
        min_ = numpy.array([item[3] for item in stats])
        max_ = numpy.array([item[2] for item in stats])

        # formatting salary on xaxis
        def _millions(x, pos):
            'Convert 20,000 to £20k'
            x = int(x / 1000)
            return f'£{x}k'    
        formatter = FuncFormatter(_millions)
        ax.xaxis.set_major_formatter(formatter)

        # plotting the line 1 points  
        ax.plot(average, labels, label = "Average",  marker='o', markevery=None) 
        # annotate averages
        for i,j in zip(average,labels):
            # formating i
            avg = i // 1000
            ax.annotate(f'£{avg}k', xy=(i,j), xytext=(7,-3), textcoords='offset points')
        ax.plot(median, labels, label = "Median") 
        ax.plot(min_, labels, label = "Min") 
        ax.plot(max_, labels,  label = "Max") 
 
        # ploting the living wage
        ax.axvline(x=22360, color='k', linestyle=':', label="Living Wage")

        # filling between lines
        ax.fill_betweenx(labels, average, max_, color='red')
        ax.fill_betweenx(labels, average, median, color='yellow')
        ax.fill_betweenx(labels, median, min_, color='green')
       
        # show a legend on the plot 
        ax.legend() 
       
        return ax


        # calculating stats for all queries
        stats = []
        for qid, qname, _, qcount in self.queries:
            try:
                dataframe, mean, median, min_, max_ = await self.calculate_salary_stats(qid)
                stats.append((qname, dataframe, max_, min_))
            except Exception:
                # the query is empty
                pass 

        # sort stats by max
        stats.sort(key=lambda item: item[2])

        # creating axes for all histogram
        fig, axes = matplotlib.pyplot.subplots(len(stats), 1, sharex=True, sharey=True)

        count = 0
        while count < len(stats):
            ax = axes[count]
            self.plot_distrib(ax, stats[count], 5000)

            ax.set_title(stats[count][0], x=-0.2,y=0.1)

            # removing left, right and top borders
            ax.yaxis.set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)

            # keeping bottom border and ticks for the last plot
            if count != len(stats) -1:
                ax.xaxis.set_visible(False)
                ax.spines['bottom'].set_visible(False)
            count += 1
        
        matplotlib.pyplot.show()


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
        

def report_salaries():
    data_type = models
    db_name = 'query-offer.db'

    async def test():
        db = await database.AsyncDB(db_name, models)
        report = await SalariesReport(db)
        await report.report_all()

    asyncio.run(test())

def report_skills():
    data_type = models
    db_name = 'query-offer.db'

    async def test():
        db = await database.AsyncDB(db_name, data_type)
        report = await SkillsReport(db)
        await report.report_all()

    asyncio.run(test())      

if __name__ == "__main__":
    report_salaries()