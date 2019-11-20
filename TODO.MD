
#############################  TODO  ############################### 

# BUG #
-> can click multiple times on search thus getting the same results mutliple times 
==> disable the button or find a way to cancel the request 

# urgent #
-> add logging 
-> add argument parser
-> move aioObject somewhere else

# logic #
-> compare query to db + last update (build relational db) 
=> retrieve from database

# view #
-> remove doubles in js 
-> add href to job titles
-> handle connection errors in the webview

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
-> auto resume (organise resume automaticaly based on the skills requirements) or % of match 
      => just like job scan : https://www.jobscan.co
-> auto apply
-> cli view (long live the cli)
-> data analysis:
      - most skills required (bag of words ?)
      - median and average salary for the query
      - color code salary (high to low) and skills (frequency) red to green to grey for unknown
