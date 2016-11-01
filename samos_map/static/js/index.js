var map = L.map('map').setView([30.0, -40.0], 3);

var markerLayerGroup = L.layerGroup().addTo(map);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 16,
    attribution: 'Map data &copy; <a href="https://openstreetmap.org"> ' +
        'OpenStreetMap</a> contributors, ' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'
}).addTo(map);

function getPins(e) {
    bounds = map.getBounds();
//    url = "/data" +
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
    map.removeLayer(markerLayerGroup);

    //add the new pins
    var markerArray = new Array(data['points'].length);
    console.log("HELLO");
    console.log(data);

    for (var i = 0; i < data['points'].length; i++) {
        if (i < 10) {
            console.log(data['points'][i])
        }
        point = data['points'][i];
        markerArray[i] = L.marker([point.lat, point.lon]).bindPopup("hey");
    }
    markerLayerGroup = L.layerGroup(markerArray).addTo(map);

    console.log("DONE");
}


map.on('dragend', getPins);
map.on('zoomend', getPins);
map.whenReady(getPins)