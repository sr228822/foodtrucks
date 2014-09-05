var map;

var endpoint = 'http://ec2.sfflux.com:4444/api/v1/foodtrucks'

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

    // make an api request with bounds and search terms TODO fill in query
    apiRequest(sw.lat(), sw.lng(), ne.lat(), ne.lng(), "");
}

/* Make a call to our backend api */
function apiRequest(start_lat, start_lng, end_lat, end_lng, query) {
    $(document).ready(function() {
        $.get(endpoint + "?start_lat=" + start_lat + "&start_lng=" + start_lng + "&end_lat=" + end_lat + "&end_lng=" + end_lng + "&query=" + query ,function(data) {parseAndDraw(data);});
    });
}

/* Called when we get our data back.  Parse the json results and draw them onto our map */
function parseAndDraw(data)
{
    // Clear the previous markers
    setMarkersMap(markers, null);
    markers = [];

    // parse data-json into a list of markers
    var js = JSON.parse(data);
    var num = js.num_returned;
    for(var i=0; i < num; i++) {
        var truck = js.results[i];
        var name = truck.Applicant;
        var latlng = new google.maps.LatLng(parseFloat(truck.Latitude), parseFloat(truck.Longitude));
        var marker = new google.maps.Marker({
            position: latlng,
            title:name,
        });
        // TODO attach a pop-up with more info on this truck?
        markers.push(marker);
    }

    // Draw all markers on the map
    setMarkersMap(markers, map);
}

/* Initialize the google map object */
function initialize() {
    var mapOptions = {
        center: new google.maps.LatLng(37.765, -122.440),
        zoom: 12
    };
    map = new google.maps.Map(document.getElementById("map-canvas"),mapOptions);

    // callback to refresh map when the bounds change
    google.maps.event.addListener(map, 'idle', function(event) {
        refreshMap();
    });

    refreshMap();
}

google.maps.event.addDomListener(window, 'load', initialize);
