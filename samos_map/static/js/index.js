$('document').ready(function() {

var timeoutHandler;
var map = L.map('map').setView([30.0, -40.0], 5);

var markerLayerGroup = L.layerGroup().addTo(map);
var osmurl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
var attrib = 'Map data &copy; <a href="https://openstreetmap.org"> ' + 
    'OpenStreetMap</a> contributors, ' + 
    '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'

var osm = new L.tileLayer(osmurl, { minZoom: 5, maxZoom: 16, attribution: attrib})
map.addLayer(osm);

var miniosm = new L.TileLayer(osmurl, {minZoom: 0, maxZoom: 13, attribution: attrib });
var mini = new L.Control.MiniMap(miniosm, { toggleDisplay: true }).addTo(map);


map.on('click', function(e) {
    console.log('click event object: '); console.log(e);
    console.log(e.latlng.lat, e.latlng.lng, map.getZoom());
    ancillaryData(e.latlng.lat, e.latlng.lng);
});


L.control.coordinates({
    position : "bottomleft", //optional default "bootomright"
    decimals : 2, //optional default 4
    decimalSeperator : ".", //optional default "."
    labelTemplateLat : "Lat: {y}", //optional default "Lat: {y}"
    labelTemplateLng : "Lon: {x}", //optional default "Lng: {x}"
    enableUserInput : true, //optional default true
    useDMS : false, //optional default false
    useLatLngOrder : true, //ordering of labels, default false-> lng-lat
    markerType : L.marker, //optional default L.marker
    markerProps : {}, //optional default {}
}).addTo(map);


var info = L.control();

info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info');
    this.update();
    return this._div;
};

info.update = function (rec) {
    if (rec != null) {
        latlon = rec.loc.split(',');
        lat = parseInt(latlon[0], 10);
        lon = parseInt(latlon[1], 10);
        map.setView([lat, lon], map.getZoom());
        console.log(rec);
    }
    this._div.innerHTML = '<h3>SAMOS record viewer</h3>' +  (rec ?
        '<b><a href="' + rec.thredds + '">' + rec.meta + '</a></b><br />' + 
        '<b>loc</b> : ' + rec.loc + '<br />' +
        '<b>SSS</b> : ' + rec.SSS + ' <b>PSU<b/><br />' +
        '<b>SST</b> : ' + rec.SST + ' <b>&#8451;<b/><br />' +
        '<b>wind_u</b> : ' + rec.wind_u + ' <b>m/s<b/><br />' +
        '<b>wind_v</b> : ' + rec.wind_v + ' <b>m/s<b/><br />' +
        '<b>wind_speed</b> : ' + rec.wind_speed + ' <b>m/s<b/><br />'
        : 'Click anywhere on map');
};

info.addTo(map);


function moveHandler() {
    removePolygon()
    window.clearTimeout(timeoutHandler);
    timeoutHandler = window.setTimeout(function() {
        map.fire('idle');
    }, 500);
}

var shownLayer, polygon;
function removePolygon() {
    if (shownLayer) {
        shownLayer.setOpacity(1);
        shownLayer = null;
    }
    if (polygon) {
        map.removeLayer(polygon);
        polygon = null;
    }
};

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

var markers;
function pinTheMap(data) {
    //clear the current pins
    if (markers != null)
        map.removeLayer(markers);


     // var clusterArray = L.markerClusterGroup({
        // iconCreateFunction: function(cluster){
            // return L.divIcon({html: '<b>' + cluster.getChildCount() + '</b>'});
        // }
    // });
    var clusterFound = 0;
    clusters = {}
    
    //add the new pins
    var markerArray = new Array(data['points'].length);
    console.log('Got ' + data['points'].length + ' data points')
    for (var i = 0; i < data['points'].length; i++) {
        point = data['points'][i];
        markerArray[i] = L.marker([point.lat, point.lon])//.bindPopup(point.idx);
        markerArray[i].ship = point.meta;
        markerArray[i].idx = point.idx;
        if (clusters[markerArray[i].ship] == null) {
            //Custom radius and icon create function
            clusters[markerArray[i].ship] = new L.markerClusterGroup({
                chunkedLoading: true,
                maxClusterRadius: 120,
                iconCreateFunction: function (cluster) {
                    var markers = cluster.getAllChildMarkers();
                    var ships = {};
                    var maxcount = 0;
                    clusterFound = 1;
                    console.log('Marker cluster group instantiated with ' + markers.length + ' records')
                    for (var i = 0; i < markers.length; i++) {
                        if (ships[markers[i].ship] == null) ships[markers[i].ship] = 1;
                        else ships[markers[i].ship]++;
                        if (ships[markers[i].ship] > maxcount) {
                            maxship = markers[i].ship;
                            maxcount = ships[maxship];
                        }
                    }
                    
                    // record ships found in query
                    console.log('Found ships: ')
                    for (var i = 0, keys = Object.keys(ships), ii = keys.length; i < ii; i++) {
                        console.log('\t' + keys[i] + ' : ' + ships[keys[i]] + ' records');
                    }
                    return L.divIcon({ html: maxship, className: 'mycluster', iconSize: L.point(40, 40) });
                },
                //Disable all of the defaults:
                spiderfyOnMaxZoom: false, showCoverageOnHover: false, zoomToBoundsOnClick: false
            });
        }
        clusters[markerArray[i].ship].addLayer(markerArray[i]);

        if (clusterFound == 0 && i < 10) {
            console.log('Point where cluster did not init: ' + 
                markerArray[i].ship + '-' + point.idx + ' ' + point.lat + ',' + point.lon)
        }
        // markerArray[i].on('click',
            // function(e, feature) {
                // this._popup.setContent(ancillaryData(this._popup));
        // });
    }

    // we add the cluster group, not the indivual points
    for (var i = 0, keys = Object.keys(clusters), ii = keys.length; i < ii; i++) {
        map.addLayer(clusters[keys[i]]);
        
        // cluster animation stuff
        clusters[keys[i]].on('clustermouseover', function (a) {
            removePolygon();

            a.layer.setOpacity(0.2);
            shownLayer = a.layer;
            polygon = L.polygon(a.layer.getConvexHull());
            map.addLayer(polygon);
        });
        clusters[keys[i]].on('clustermouseout', removePolygon);
        
        clusters[keys[i]].on('clusterclick', function (a) {
            a.layer.setOpacity(0.7);
            console.log('Clusterclick event object: '); console.log(a);
            ancillaryData(a.latlng.lat, a.latlng.lng);
        });
    }

    // markerLayerGroup = L.layerGroup(markerArray).addTo(map);
}

function ancillaryData(lat, lon) {
    // idx corresponds to where this point is in the server's data
    url = "/map/data?lat=" + lat + "&lon=" + lon;
    console.log(url);
    var text = "";
    $.getJSON(url, function(data) {
        // text = data['meta'] + '\n' + data['time'];
        console.log(data);
        info.update(data);
    });
    map.fire('idle');
    // console.log(text);
    // return text;
}


map.on('zoomend dragend', moveHandler);
map.on('idle', getPins);
map.whenReady(getPins)

});