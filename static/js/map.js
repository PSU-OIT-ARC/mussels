$(document).ready(function(){
    var styles = [
      {
        "elementType": "labels",
        "stylers": [
          { "visibility": "off" }
        ]
      }
    ];
    var mapOptions = {
        center: new google.maps.LatLng(0, 0),
        zoom: 1,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById("map"), mapOptions);
    map.setOptions({styles: styles})

    // center the map around the US
    // http://stackoverflow.com/questions/2936960/google-maps-api-load-the-us
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({'address': 'US'}, function (results, status) {
         map.fitBounds(results[0].geometry.viewport);               
    }); 

    var kmlLayer = new google.maps.KmlLayer('<PUBLIC URL>')
    kmlLayer.setMap(map)
});

