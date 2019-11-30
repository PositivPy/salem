
#############################  TODO  ############################### 

# BUG #
-> can click multiple times on search thus getting the same results mutliple times ==> disable the button or find a way to cancel the request -> a way to cancel query : https://stackoverflow.com/questions/34710835/proper-way-to-shutdown-asyncio-tasks
-> maybe, problem with coroutine not being really async, the parse function should probably be an async generator

-> 11-28 17:59:50 aiosqlite 		   ERROR   returning exception UNIQUE constraint failed: OFFERS.title, OFFERS.company, OFFERS.min_£
Traceback (most recent call last):
sqlite3.IntegrityError: UNIQUE constraint failed: OFFERS.title, OFFERS.company, OFFERS.min_£
11-28 17:59:50 salem/model.py 		   WARNING Offer already exsists in database
11-28 17:59:51 asyncio 		   ERROR   Task exception was never retrieved
future: <Task finished coro=<<async_generator_athrow without __name__>()> exception=TypeError('cannot unpack non-iterable NoneType object')>
Traceback (most recent call last):
GeneratorExit

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
TypeError: cannot unpack non-iterable NoneType object
11-28 17:59:51 salem/http_.py 		   WARNING No internet connection
11-28 17:59:51 salem/http_.py 		   WARNING No internet connection
11-28 17:59:51 salem/http_.py 		   WARNING No internet connection



# urgent #
-> web

# web #
-> sort by match
-> find a solution for <th>
-> move salary under match
-> handle errors in the webview (connection drops)
-> stats :
      - results nb
      - time
      - mean/median salary for the query
      - average match for query

# model #
-> integrate retrival into the controller
-> database reporting tools (testing)

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
-> move match calculation to the client
-> Indeed still not answering
-> auto apply
-> cli view (long live the cli)
-> data analysis:
      - query insights via API
      - most skills required (bag of words ?)
      - color code salary (high to low) and skills (frequency) red to green to grey for unknown
