function sortResults() {
    // https://stackoverflow.com/questions/5066925/javascript-only-sort-a-bunch-of-divs
    var toSort = document.getElementById('results').children;
    toSort = Array.prototype.slice.call(toSort, 0);

    toSort.sort(function(a, b) {
        // a and b are offer divs
        var aord = +a.getAttribute("salary");
        var bord = +b.getAttribute("salary");

        return (aord <= bord) ? 1 : -1;
    });

    var parent = document.getElementById('results');
    parent.innerHTML = "";

    for(var i = 0, l = toSort.length; i < l; i++) {
        parent.appendChild(toSort[i]);
    }
}

function socketHandler() {
    toggleLoaderOn()
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
        toggleLoaderOff()
        // on message from server : build offers' div
        var data = event.data;
        var received = JSON.parse(data);

        // creating and formating the offers' divs as they come
        var offer = document.createElement('div');
        salary_min = received['salary_min'];
        if (salary_min == null) {
            salary_min = '0'
        }
        offer.setAttribute("class", "offers");
        offer.setAttribute("salary", salary_min);
        // TODO : prettify the skills section
        offer.innerHTML = '<h2>' + received['title'] + '</h2><h3>' + received['company'] + '</h3> <p>Salary: ' + salary_min + '<br>' + received['skills'] + '</p>';
        resultDiv.appendChild(offer);
        // each time we add an offer, we sort them by salary
        sortResults()
    }
}

function toggleLoaderOn() {
    var x = document.getElementById("loader");
    if (x.style.display === "none" || x.style.display === '') {
      x.style.display = "block";
    }
  }

function toggleLoaderOff() {
    var x = document.getElementById("loader");
    if (x.style.display === "block") {
        x.style.display = "";
      }
}