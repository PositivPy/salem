
#############################  TODO  ############################### 

BUG : There is a problem with the scraper not getting every pages 
Could be related to session drops or the way the listing urls are generated
from common self.params

-> add logging (how did I manage so far?)

-> argument parser
-> sort offer divs in js
-> compare query to db + last update (build relational db)  
-> move aioObject somewhere else
-> add href to job titles
-> virtual environement

To think about :
-> a way to remove doubles 
-> auto resume (organise resume automaticaly based on the skills requirements)
-> auto apply
-> cli view (long live the cli)
-> data analysis:
      - most skills required
      - median and average salary for the query
-> could make an API out of this by sending JSON from socket 
   rather than formated divs. The formating will be up to the client
