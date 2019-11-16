#!/usr/bin/env python3

header = '''
<!DOCTYPE html>
<body>
<img src="/static/header_logo.png" alt="Icon" height="70" width="180"> '''

footer = "</body></html>"

search_bar = '''
    <form action="/search/">
      <input type="text" placeholder="Search.." name="q" value="{previous_query}">
      <button type="submit">Submit</button>
    </form>
'''

offer_div = '''<br>
<h3> {title} </h3>
<p> Company: {company} <br> Salary: {salary} <br> {skills} <br>
'''

def render_index():
    # there is no previous query for now
    s_bar = search_bar.format(previous_query='')
    return header + s_bar + footer

def render_results(query, offers):
    res = str()
    for offer in offers:
        res += offer_div.format(title=offer.title, company=offer.company, 
                                salary=offer.salary, skills=offer.skills)
    s_bar = search_bar.format(previous_query=query)
    return header + s_bar + res + footer
