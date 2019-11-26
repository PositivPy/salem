function socketHandler() {
    toggleLoaderOn()
    var resultDiv = document.getElementById("tresults");
    
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

        var offer = formatOffer(received)

        resultDiv.appendChild(offer);
        // each time we add an offer, we sort them by salary
        sortResults()
    }
}

function formatOffer(data) {
    // creating and formating the offers' divs as they come
    var offer = document.createElement('tr');

    offer.setAttribute("class", "offers");
    offer.setAttribute("salary", data['salary_min']);

    var match_div = formatSkillsMatch(data['match'])

    // TODO : prettify this skills section
    var text = document.createElement('div');
    text.setAttribute('class', 'text')
    
    // Building the skill string from array
    var skillString = ''
    for (i = 0; i < data['skills'].length; i++) {
        skillString += ' ' + data['skills'][i] + ','
    }
    skillString = skillString.charAt(0).toUpperCase() + skillString.slice(1); 
    
    // salary can be null sometimes if it isn't present 
    // in Indeed TODO: always send non-null values
    var minSalary = data['salary_min'];
    if (minSalary === "null") {
        minSalary = 0;
    }

    text.innerHTML = "<a href='" + data['url'] + "'>" + '<h2>' + data['title'] + '</h2></a><h3>' + data['company'] + '</h3> <p>Salary: ' + minSalary + '<br>' + skillString + '</p>';

    offer.appendChild(match_div)
    offer.appendChild(text)

    return offer
}

function formatSkillsMatch(p) {
    var match = document.createElement('tr');

    /* Building class */
    var class_ = "progress-circle"
    if (p > 50) {
        class_ += " over50"
    }
    class_ += ' p' + p

    match.setAttribute("class", class_);
    match.innerHTML = '<span>' + p + '%</span>'

    var clipper = document.createElement('div');
    clipper.setAttribute("class", "left-half-clipper");

    var type_ = document.createElement('div');
    type_.setAttribute("class", "first50-bar");
    clipper.appendChild(type_);

    var value_bar = document.createElement('div');
    value_bar.setAttribute("class", 'value-bar');
    clipper.appendChild(value_bar);

    match.appendChild(clipper);
    
    return match
}

function sortResults() {
    // https://stackoverflow.com/questions/5066925/javascript-only-sort-a-bunch-of-divs
    var toSort = document.getElementById('tresults').children;
    toSort = Array.prototype.slice.call(toSort, 0);
    toSort.sort(function(a, b) {
        // a and b are offer divs
        var aord = +a.getAttribute("salary");
        var bord = +b.getAttribute("salary");

        return (aord <= bord) ? 1 : -1;
    });

    var parent = document.getElementById('tresults');
    parent.innerHTML = "";

    for(var i = 0, l = toSort.length; i < l; i++) {
        parent.appendChild(toSort[i]);
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