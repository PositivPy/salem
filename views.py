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
<p> {salary} <br> {skills} <br>
'''
class TemplateEngine:

    def render_index(self):
        return header + search_bar + footer
    
    def render_results(self, offers):
        res = str()
        for offer in offers:
            res += offer_div.format(title=offer.title, salary=offer.salary, skills=offer.skills)
        return header + search_bar + res + footer