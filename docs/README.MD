Can I apply automatically to ads with certainty ?
- The indeed/reed suggestions problem, what wages should I apply to ?
    => extracting relevant job offers from wages
- Comparing CVs to Offer's 
    => extracting most important skills 
- pitfalls, ameloriation 


SUMMARY

In an effort to seek employment and improve my programming and analytical skills, I spent a month creating a job market analysis tool capable of applying precisely to job offers I would myself consider.

ABSTRACT 

The online job market represent % of all applications sent to companies. The application process has been streamlined enough that the longest part of applying for a vacancy is still... searching. Picking the offers from a dense stream of haystack and text based search, while obviously practical, is rather limited (see part recursive) and biased (see part X) as well.
Moreover, not all offers fits an applicant's interest or expectation. And an applicant does not necessarely fit all requirements. Thus, it would be conterproductive for a job seeker to apply to all offers regardless.
Is it possible to create a faster type of search, with different metrics ?

TOOLS

1. Libraries:
In an effort to keep dependencies low, few libraries are to be installed.

For the App/Scraper;
Aiosqlite and aiohttp for async methods waiting for IO (waiting for a web page or a database lock)
Note: aiohttp is orders of magnitudes faster than requests but is quite brutal on servers and local coffee shops (over 200 requests in less than 10 seconds). 

For the reports only;
Matplotlib for plotting. It is a bit of a pain to use. For example a Figure does not have the same properties as a pyplot or an Axe and an inserted Axe does not share it's properties with an Axe somehow. 

Pandas and numpy for fast data wrangling. While not used very much here, it is optimal for operations on structured data. 

That is it.

2. The Scraper:
Download, parsing and database

3. Web Socket:
Why, how, use cases

ANALYSIS

1. Skills extraction and matching:
Gazeteers vs machine learning
2. Wages analysis:
how does different plotting techniques create biases





The case for a brutal downloader in this situation:
Small scale operation. I'm sure Indeed is prepared for these sorts of situations. 
Anyway, if a few frames drop, the next query will scrape them, thus a timeout is set (10sec). 


skills extractions 
Just like salaries, I need to be able to separate common skills and specific offer skills 
