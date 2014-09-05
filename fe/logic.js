var map;
var query = "";
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

    // make an api request with bounds and search terms
    apiRequest(sw.lat(), sw.lng(), ne.lat(), ne.lng(), query);
}

/* Make a call to our backend api */
function apiRequest(start_lat, start_lng, end_lat, end_lng, query) {
    $(document).ready(function() {
        $.get(endpoint + "?start_lat=" + start_lat + "&start_lng=" + start_lng + "&end_lat=" + end_lat + "&end_lng=" + end_lng + "&perpage=5000&food=" + query ,function(data) {parseAndDraw(data);});
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
    console.log("Got " + num + " trucks");
    for(var i=0; i < num; i++) {
        var truck = js.results[i];
        var name = truck.Applicant;
        var latlng = new google.maps.LatLng(parseFloat(truck.Latitude), parseFloat(truck.Longitude));
        var marker = new google.maps.Marker({
            position: latlng,
            title:name,
        });

        var contentStr = '<h3>' + name + '</h3>' +
                      truck.Address + '<br>' +
                      truck.FoodItems;
        var infowindow = new google.maps.InfoWindow({
            content: contentStr
        });
        google.maps.event.addListener(marker, 'click', (function(marker,contentStr,infowindow){
            return function() {
                infowindow.setContent(contentStr);
                infowindow.open(map,marker);
            };
        })(marker,contentStr,infowindow));

        markers.push(marker);
    }

    // Draw all markers on the map
    setMarkersMap(markers, map);
}

function processQuery()
{
    query = document.getElementById('foodquery').value
    console.log("processing query " + query);
    refreshMap();
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
