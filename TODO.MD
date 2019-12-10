
#############################  TODO  ############################### 

# BUG #
-> can click multiple times on search thus getting the same results mutliple times ==> disable the button or find a way to cancel the request -> a way to cancel query : https://stackoverflow.com/questions/34710835/proper-way-to-shutdown-asyncio-tasks

# web #
-> fix undefined
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
-> could use the reports or create a new page for reports 

# database #
-> fix insert offer for the new model 

# nlp # --> move to analyse.py
-> parse qualifications from description
-> parse education
-> parse benefits from description
-> parse salary from description

# report #
-> add logger
-> move all the analysis to nlp
-> arg parser
-> advanced skills report
-> optimize matplotlib

# To think about #
-> auto apply
-> cli view (long live the cli)

# other #
-> type a report
-> type a CV
