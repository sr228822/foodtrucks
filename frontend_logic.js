var map;
var curZoom;

var endpoint = 'http://localhost:5000/api/v1/foodtrucks'

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
    // TODO get the bounds of the map

    // TODO get current search term

    // TODO make an api request with bounds and search terms
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
    curZoom = map.getZoom();

    google.maps.event.addListener(map, 'zoom_changed', function() {
        if (curZoom != map.getZoom()) {
            curZoom = map.getZoom();
            console.log("zoom = " + curZoom);
            refreshMap();
        }
    });

    // TODO add a callback to refresh map when the bounds change
    //   should I remove the zoom callback if bounds change on a zoom?

    refreshMap();
}

google.maps.event.addDomListener(window, 'load', initialize);
