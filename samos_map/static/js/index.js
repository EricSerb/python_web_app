$('document').ready(function() {

var timeoutHandler;
var map = L.map('map').setView([30.0, -40.0], 3);

var markerLayerGroup = L.layerGroup().addTo(map);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 16,
    attribution: 'Map data &copy; <a href="https://openstreetmap.org"> ' +
        'OpenStreetMap</a> contributors, ' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'
}).addTo(map);

function moveHandler() {
    window.clearTimeout(timeoutHandler);
    timeoutHandler = window.setTimeout(function() {
        map.fire('idle');
    }, 500);
}

function getPins(e) {
    bounds = map.getBounds();
    url = "/map/data" +
        '?S=' + bounds.getSouthWest().lat +
        '&W=' + bounds.getSouthWest().lng +
        '&N=' + bounds.getNorthEast().lat +
        '&E=' + bounds.getNorthEast().lng;
    console.log(url);
    $.get(url, pinTheMap, "json")
}

function pinTheMap(data) {
    //clear the current pins
    // map.removeLayer(markerLayerGroup);

    //add the new pins
    var markerArray = new Array(data['points'].length);

    for (var i = 0; i < data['points'].length; i++) {
        point = data['points'][i];
        markerArray[i] = L.marker([point.lat, point.lon]).bindPopup(point.idx);
        console.log(markerArray[i]);
        markerArray[i].on('click',
            function(e, feature) {
                this._popup.setContent(ancillaryData(this._popup));
        });
        
    }
    markerLayerGroup = L.layerGroup(markerArray).addTo(map);
}

function ancillaryData(popup) {
    // idx corresponds to where this point is in the server's data
    url = "/map/data?idx=" + popup._content;
    console.log(url);
    var text = "";
    $.getJSON(url, function(data) {
        text = data['meta'] + '\n' + data['time'];
        console.log(text);
    });
    console.log(text);
    return text;
}


map.on('zoomend dragend', moveHandler);
map.on('idle', getPins);
map.whenReady(getPins)

});