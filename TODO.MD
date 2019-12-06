
#############################  TODO  ############################### 

# BUG #
-> can click multiple times on search thus getting the same results mutliple times ==> disable the button or find a way to cancel the request -> a way to cancel query : https://stackoverflow.com/questions/34710835/proper-way-to-shutdown-asyncio-tasks
-> maybe, problem with coroutine not being really async, the parse function should probably be an async generator


# urgent #
-> organisation
-> web

# web #
-> sort by match
-> find a solution for <th>
-> move salary under match
-> handle errors in the webview (Eror 404)
-> move match calculation to the web client
-> enable receiving stats by checking type in message:
      - results nb
      - time
      - mean/median salary for the query
      - average match for query

# database #
-> fix insert offer for the new model 

# nlp # --> move to analyse.py and merge with test.py
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
-> auto apply
-> cli view (long live the cli)
-> data analysis:
      - query insights via API
      - most skills required (bag of words ?)
      - color code salary (high to low) and skills (frequency) red to green to grey for unknown
