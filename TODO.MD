
#############################  TODO  ############################### 

# BUG #
-> can click multiple times on search thus getting the same results mutliple times ==> disable the button or find a way to cancel the request -> a way to cancel query : https://stackoverflow.com/questions/34710835/proper-way-to-shutdown-asyncio-tasks
-> maybe, problem with coroutine not being really async, the parse function should probably be an async generator


# urgent #
-> web

# web #
-> something going wrong with offer._asdict() not being parsed properly by json.dumps()
-> sort by match
-> find a solution for <th>
-> move salary under match
-> handle errors in the webview (connection drops)
-> stats :
      - results nb
      - time
      - mean/median salary for the query
      - average match for query

# database #
-> database reporting tools (testing)
-> fix insert offer for the new model 

# nlp #
-> parse qualifications from description
-> parse education
-> parse benefits from description
-> parse salary from description

# organisation #
-> testing suite
-> virtual environement
-> README.MD
-> move everything to a /src

# To think about #
-> remove doubles
-> move match calculation to the  web client
-> Indeed still not answering
-> auto apply
-> cli view (long live the cli)
-> data analysis:
      - query insights via API
      - most skills required (bag of words ?)
      - color code salary (high to low) and skills (frequency) red to green to grey for unknown
