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

    var infowindow = new google.maps.InfoWindow({
        content: '',
        pixelOffset: new google.maps.Point(0, 0),
    });

    $.getJSON("/json", function(data){
        for(var i = 0; i < data.length; i++){
            var row = data[i];
            var point = new google.maps.LatLng(row.the_geom_plain[1], row.the_geom_plain[0]);
            var icon = {
                url: '/static/img/kml_icons/' + row.style + ".png",
                anchor: new google.maps.Point(23, 25),
                scaledSize: new google.maps.Size(45, 45),
            }

            var marker = new google.maps.Marker({
                position: point,
                map: map,
                title: "foo",
                icon: icon,
            })


            with({marker: marker, row:row}){
                google.maps.event.addListener(marker, 'click', function(){
                    infowindow.setContent("<strong>" + row.substrate_id + "</strong>")
                    infowindow.open(map, marker);
                });
            }

        }

    })


});

