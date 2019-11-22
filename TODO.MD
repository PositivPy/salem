
#############################  TODO  ############################### 

# BUG #
-> can click multiple times on search thus getting the same results mutliple times ==> disable the button or find a way to cancel the request 
-> unable to recover from aiohttp ssl.SSLError: [SSL: KRB5_S_INIT] application data after close notify ==> upgrade to 3.8 or https://github.com/aio-libs/aiohttp/issues/3535.

# urgent #
-> compare query to db + last update (build relational db) 
=> retrieve from database
-> move aioObject somewhere else

# view #
-> remove doubles in js 
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
-> a way to cancel query
-> ask Indeed for api key again 
-> replace namedTuples; it's annoying most of the time ; Dataframe might be Big-O expensive tho
-> auto apply
-> cli view (long live the cli)
-> data analysis:
      - query insights 
      - most skills required (bag of words ?)
      - median and average salary for the query
      - color code salary (high to low) and skills (frequency) red to green to grey for unknown
