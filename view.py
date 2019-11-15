#!/usr/bin/env python3

header = "<!DOCTYPE html><body>"
footer = "</body></html>"

search_bar = '''
    <form action="/search/">
      <input type="text" placeholder="Search.." name="q">
      <button type="submit">Submit</button>
    </form>
'''

offer_div = '''<br>
<h1> {title} </h1>
<p> Company: {company} <br> Salary: {salary} <br> {skills} <br>
'''

def render_index():
    return header + search_bar + footer

def render_results(offers):
    res = str()
    for offer in offers:
        res += offer_div.format(title=offer.title, company=offer.company, salary=offer.salary, skills=offer.skills)
    return header + search_bar + res + footer
