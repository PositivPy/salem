function sortResults() {
    // https://stackoverflow.com/questions/5066925/javascript-only-sort-a-bunch-of-divs
    var toSort = document.getElementById('results').children;
    toSort = Array.prototype.slice.call(toSort, 0);

    toSort.sort(function(a, b) {
        // a and b are offer divs
        var aord = +a.getAttribute("salary");
        var bord = +b.getAttribute("salary");
        // two elements never have the same ID hence this is sufficient:
        return (aord <= bord) ? 1 : -1;
    });

    var parent = document.getElementById('results');
    parent.innerHTML = "";

    for(var i = 0, l = toSort.length; i < l; i++) {
        parent.appendChild(toSort[i]);
    }
}

function socketHandler() {
    var resultDiv = document.getElementById("results");
    
    // cleaning up the previous results
    while (resultDiv.firstChild) {
        resultDiv.removeChild(resultDiv.firstChild);
    }
    var Socket = new WebSocket("ws://localhost:8080/search");
    
    Socket.onopen = function() {
        var query = document.getElementById("searchBarQuery").value;
        var location = document.getElementById("searchBarLocation").value;

        if (!location) {
            location = "London";
            var loc = document.getElementById("searchBarLocation");
            loc.value ="London";
        }
        
        var responseObject = {"query" : query, "location" : location};
        var responseJson = JSON.stringify(responseObject)

        Socket.send(responseJson);

    }

    Socket.onmessage = function (event) {
        // on message from server : build offers' div
        var data = event.data;
        var received = JSON.parse(data);

        var offer = document.createElement('div');
        offer.setAttribute("class", "offers");
        offer.setAttribute("salary", received['salary_min']);
        // TODO : prettify the skills section
        offer.innerHTML = '<h2>' + received['title'] + '</h2><h3>' + received['company'] + '</h3> <p>Salary:' + received['salary_min'] + '<br>' + received['skills'] + '</p>';
        resultDiv.appendChild(offer);
        // each time we add an offer, we sort them by salary
        sortResults()
    }
}