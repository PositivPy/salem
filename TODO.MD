
#############################  TODO  ############################### 

# BUG #
-> can click multiple times on search thus getting the same results mutliple times ==> disable the button or find a way to cancel the request 
or close socket connection
-> unable to recover from aiohttp ssl.SSLError: [SSL: KRB5_S_INIT] application data after close notify ==> upgrade to 3.8 or https://github.com/aio-libs/aiohttp/issues/3535.
-> match skills over 50% getting clipped

# urgent #
-> BUILDING DATABASE :
The offers are still not getting saved into the db because I changed the JobOffer's parameters in jobs.py thus no relations can be built yet
Salary min and max still not properly separated thus view -1
All Queries:
[(1, 'junior python developer', '2019-11-23 18:36:19', 1), (2, 'junior python analyst', '2019-11-23 18:36:19', 1), (3, 'junior quant developer', '2019-11-23 18:36:19', 1), (4, 'junior quant analyst', '2019-11-23 18:36:19', 1), (5, 'mid python developer', '2019-11-23 18:36:19', 1), (6, 'mid python analyst', '2019-11-23 18:36:19', 1), (7, 'mid quant developer', '2019-11-23 18:36:19', 1), (8, 'mid quant analyst', '2019-11-23 18:36:19', 1), (9, 'bartender', '2019-11-23 18:37:42', 1), (10, 'waiter', '2019-11-23 18:39:16', 3), (11, 'manager', '2019-11-23 18:46:54', 2), (12, 'researcher', '2019-11-23 20:03:43', 6)]
All Offers
[]
All relations
[]

-> move aioObject somewhere else / still don't know 

# view #
-> REVAMP :
Much better in a table for easy alignments
Everything is pretty buggy still:
      - not sorting 
      - no salary
      - no match
      - no skills
      - th appears when not wanted and vice-versa
But I'm pretty sure it's the way forward.
-> add href to job titles
-> handle errors in the webview

# nlp #
-> parse qualifications from description
-> parse salary from description

# organisation #
-> virtual environement
-> README.MD
-> move everything to a /src

# To think about #
-> remove doubles
-> parse education 
-> a way to cancel query
-> ask Indeed for api key again / as soon as querying from db works 
-> replace namedTuples; it's annoying most of the time ; Dataframe might expensive tho
-> auto apply
-> cli view (long live the cli)
-> data analysis:
      - query insights 
      - most skills required (bag of words ?)
      - median and average salary for the query
      - color code salary (high to low) and skills (frequency) red to green to grey for unknown
