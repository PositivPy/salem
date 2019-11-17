
import aiohttp.web
import asyncio

header = '''
<!DOCTYPE html>
<body>
<img src="/static/header_logo.png" alt="Icon" height="70" width="180">
'''

search_bar = '''
    <form action="javascript:WebSocketTest()">
      <input id="searchBar.query" type="text" placeholder="What...">
      <input id="searchBar.location" type="text" placeholder="Where..." value="London">
      <button type="submit">Submit</button>
    </form>
'''

footer = "</body></html>"

script = '''<script type = "text/javascript">
function WebSocketTest() {
    var resultDiv = document.getElementById("results");

    var Socket = new WebSocket("ws://localhost:8080/socket");
    
    Socket.onopen = function() {
        var query = document.getElementById("searchBar.query").value;
        var location = document.getElementById("searchBar.location").value;

        var responseObject = {"query" : query, "location" : location};
        var responseJson = JSON.stringify(responseObject)

        Socket.send(responseJson);

    }

    Socket.onmessage = function (event) {
        var received = event.data;
        var offer = document.createElement('offer');

        offer.innerHTML = '<p>' + received + '</p>';
        resultDiv.appendChild(offer);
    }
}
</script>
'''

offer_div = '''<br>
<h3> {title} </h3>
<p> Company: {company} <br> Salary: {salary} <br> {skills} <br>
'''

body = '''   
<body>
    <div id = "results">
    </div>  
</body> 
'''

async def socket(request):
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)
    print("Websocket ready !")
    query = None
    async for msg in ws :
        query = msg.json()
        break

    for _ in range(10):
        # send data
        await ws.send_str(f'Hello {_}')
        await asyncio.sleep(2)
    # close the websocket
    await ws.close()
    print("Websocket closed.")

async def index(request):
    resp = header + search_bar + script + body + footer
    return aiohttp.web.Response(text=resp, content_type='text/html')

if __name__=="__main__":
    app = aiohttp.web.Application()
    app.add_routes([aiohttp.web.get('/socket', socket),
                    aiohttp.web.get('/', index)])
    app.router.add_static('/static/', path='./views/static/')
    aiohttp.web.run_app(app)