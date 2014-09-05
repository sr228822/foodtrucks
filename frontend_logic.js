var map;

var endpoint = 'http://ec2.sfflux.com/api/v1/foodtrucks'

// List of all gmap markers
var markers = [];

/* A helper function to set (or clear) a set of markers to a map */
function setMarkersMap(markers, map)
{
    for (var i = 0; i < markers.length; i++) {
        markers[i].setMap(map);
    }
}

/* Trigger a refresh of our map marker data */
function refreshMap(force) {
    var bounds = map.getBounds();
    var ne = bounds.getNorthEast();
    var sw = bounds.getSouthWest();
    console.log("Refresh map " + ne.lat() + "," + ne.lng());

    // TODO get current search term

    // TODO make an api request with bounds and search terms
    apiRequest(sw.lat(), sw.lng(), ne.lat(), ne.lng(), "");
}

function apiRequest(start_lat, start_lng, end_lat, end_lng, query) {
    $(document).ready(function() {
        $.get(endpoint + "?start_lat=" + start_lat + "&start_lng=" + start_lng + "&end_lat=" + end_lat + "&end_lng=" + end_lng + "&query=" + query ,function(data) {drawApiResults(data);});
    });
}

function drawApiResults(data)
{
    // Clear the previous markers
    setMarkersMap(markers, null);
    markers = null;

    // TODO parse data-json into a list of markers

    // TODO add those markers to markers list, draw them on map
}

/* Initialize the google map object */
function initialize() {
    var mapOptions = {
        center: new google.maps.LatLng(37.765, -122.440),
        zoom: 12
    };
    map = new google.maps.Map(document.getElementById("map-canvas"),mapOptions);

    // TODO add a callback to refresh map when the bounds change
    google.maps.event.addListener(map, 'idle', function(event) {
        refreshMap();
    });

    refreshMap();
}

google.maps.event.addDomListener(window, 'load', initialize);
