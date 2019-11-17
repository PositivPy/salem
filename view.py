#!/usr/bin/env python3

import asyncio
import aiohttp.web

header = '''
<!DOCTYPE html>
<body>
'''

search_bar = '''
<div class="center" id="header">
    <img class="img center" src="/static/header_logo.png" alt="zalem">
    <div align="center">
    <form action="javascript:querySocket()">
            <input id="searchBar.query" type="text" placeholder="What...">
            <input id="searchBar.location" type="text" placeholder="Where..." value="London">
            <input id="button" type="image" src="/static/search.png" alt="submit">
    </form>
    </div>
</div>
'''

css = '''
<style>
.center {
  display: block;
  margin-left: auto;
  margin-right: auto;
}
.offers {
    margin-left: 150px;
    max-width: 70%;
}
#header {
    width: 50%;
}

#button {
    width: 3%;
    vertical-align: middle;
    margin-left: 3px;
}
input[type="text"] {
    font-size: 15px;
}
.form {
    display: inline-block;
    margin: auto;
}

.img {
    width: 50%;
}

h2 {
    font-size: 20px;
    color: blue;
    white-space: pre-wrap;
    line-height: 0.7;
}

h3 {
    font-size: 15px;
    color: green;
    white-space: pre-wrap;
    line-height: 0;
}

p {
    font-size: 15px;
    white-space: pre-wrap;
}

</style>

'''

script = '''
<script type = "text/javascript">
function querySocket() {
    var resultDiv = document.getElementById("results");
    
    // cleaning up the previous results
    while (resultDiv.firstChild) {
        resultDiv.removeChild(resultDiv.firstChild);
    }
    var Socket = new WebSocket("ws://localhost:8080/search");
    
    Socket.onopen = function() {
        var query = document.getElementById("searchBar.query").value;
        var location = document.getElementById("searchBar.location").value;

        var responseObject = {"query" : query, "location" : location};
        var responseJson = JSON.stringify(responseObject)

        Socket.send(responseJson);

    }

    Socket.onmessage = function (event) {
        var received = event.data;
        var offer = document.createElement('div');
        offer.setAttribute("class", "offers");

        offer.innerHTML = received;
        resultDiv.appendChild(offer);
    }
}
</script>
'''

footer = "</body></html>"

offer_div = '''
<br>
<h2>{title}</h2>
<h3>{company}</h3> 
<p>Salary: {salary} <br>{skills}</p>
'''

body = '''   
<body>
    <div id = "results">
    </div>  
</body> 
'''
class WebView:
    def __init__(self, controller_interface):
        self.query_controller = controller_interface

    def run(self):
        app = aiohttp.web.Application()
        app.add_routes([aiohttp.web.get('/search', self.socket),
                        aiohttp.web.get('/', self.home)])
        app.router.add_static('/static/', path='./views/static/')
        aiohttp.web.run_app(app)

    async def socket(self, request):
        # create a socket
        ws = aiohttp.web.WebSocketResponse()
        await ws.prepare(request)
        print("Websocket ready !")

        # client sends the query as soon as the connection is open
        data = None
        async for msg in ws :
            data = msg.json()       #  = {'query' : _, 'location': _ }
            break
        print(data['query'])
        async for offer in self.query_controller(data['query'], data['location']):
            # building the offer's div
            res_div = offer_div.format(title=offer.title, company=offer.company, 
                                    salary=offer.salary, skills=offer.skills)
            # sending the resulting string 
            await ws.send_str(res_div)

        # close the websocket once done 
        await ws.close()
        print("Websocket closed.")

    async def home(self, request):
        resp = header  + search_bar + script + body + css + footer
        return aiohttp.web.Response(text=resp, content_type='text/html')

