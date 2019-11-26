
#############################  TODO  ############################### 

# BUG #
-> can click multiple times on search thus getting the same results mutliple times ==> disable the button or find a way to cancel the request 
or close socket connection
-> problem with coroutine not being really async, the parse function should probably be async generators

# urgent #
-> testing suite

# http #
-> implement retries

# web #
-> find a solution for <th>
-> move salary under match
-> sort by match
-> handle errors in the webview (connection drops)

# model #
-> database management tools

# nlp #
-> parse qualifications from description
-> parse education
-> parse benefits from description
-> parse salary from description

# organisation #
-> virtual environement
-> README.MD
-> move everything to a /src

# To think about #
-> remove doubles
-> a way to cancel query
-> confirmed email to Indeed
-> replace namedTuples; it's annoying most of the time ; Dataframe might expensive tho
-> auto apply
-> cli view (long live the cli)
-> data analysis:
      - query insights 
      - most skills required (bag of words ?)
      - median and average salary for the query
      - color code salary (high to low) and skills (frequency) red to green to grey for unknown
