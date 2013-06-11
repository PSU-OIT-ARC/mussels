var map = null;
var markers = [];
var infoWindow = null;
var clusters = {}
$(document).ready(function(){
    // turn off labels
    var styles = [
      {
        "elementType": "labels",
        "stylers": [
          { "visibility": "off" }
        ]
      }
    ];

    // map options
    var mapOptions = {
        center: new google.maps.LatLng(0, 0),
        zoom: 1,
        mapTypeId: google.maps.MapTypeId.TERRAIN,
        streetViewControl: false,
    };
    // create the map
    map = new google.maps.Map(document.getElementById("map"), mapOptions);
    map.setOptions({styles: styles})
    map.controls[google.maps.ControlPosition.RIGHT_TOP].push(document.getElementById("legend"))
    map.controls[google.maps.ControlPosition.RIGHT_TOP].push(document.getElementById("layers"))

    // center the map around the US
    // http://stackoverflow.com/questions/2936960/google-maps-api-load-the-us
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({'address': 'US'}, function (results, status) {
         map.fitBounds(results[0].geometry.viewport);               
    }); 

    // this will be the balloon window that appears when a marker is clicked
    infoWindow = new google.maps.InfoWindow({
        content: '',
    });

    markers = [];
    fetchMarkers(renderMarkers, {});
    $('#apply-button').click(applyClick)
});

function applyClick(){
    clear()
    var statuses = []
    $('.status-checkbox:checked').each(function(){
        statuses.push($(this).val());
    });
    if(statuses.length == 0){
        // jQuery won't create a querystring with an empty array, so we add something to it
        statuses.push("lame") 
    }
    fetchMarkers(renderMarkers, {"statuses": statuses})
}

function clear(){
    for(var i = 0; i < markers.length; i++){
        markers[i].setMap(null);
    }
    markers = []

    for(var k in clusters){
        clusters[k].clearMarkers()
        clusters[k].redraw()
    }
    clusters = {}
}

function fetchMarkers(onDone, kwargs){
    $.getJSON("/json", kwargs, function(data){
        for(var i = 0; i < data.length; i++){
            var row = data[i];
            // build the marker
            var marker = markerFactory(row);
            markers.push(marker);
        }

        onDone()
    })
}

function renderMarkers(){
    var markers_grouped_by_status = {}
    for(var i = 0; i < markers.length; i++){
        var marker = markers[i];
        // init the array inside the cluster
        if(!(marker.info.status_key in markers_grouped_by_status)){
            markers_grouped_by_status[marker.info.status_key] = []
        }

        // add this marker to the right cluster
        markers_grouped_by_status[marker.info.status_key].push(marker);
    }

    // now draw all the clusters on the map
    clusterByStatus(markers_grouped_by_status, Object.keys(markers_grouped_by_status))
}

// draws a set of clusters on the map
function clusterByStatus(groups, keys){
    for(var i = 0; i < keys.length; i++){
        var k = keys[i];
        var cluster_img = "/static/img/kml_cluster/status_" + k
        clusters[k] = new MarkerClusterer(map, groups[k], {
            maxZoom:8,
            minimumClusterSize: 6,
            styles: [
                {
                    url: cluster_img + "_3.png",
                    height: 28,
                    width: 28,
                    anchor: [0, 0],
                    textColor: "#000",
                    textSize: 14,
                },
                {
                    url: cluster_img + "_2.png",
                    height: 36,
                    width: 36,
                    anchor: [0, 0],
                    textColor: "#000",
                    textSize: 14,
                },
                {
                    url: cluster_img + "_1.png",
                    height: 42,
                    width: 42,
                    anchor: [0, 0],
                    textColor: "#000",
                    textSize: 14,
                },
            ]
        });
    }
}

function markerFactory(row){
    // the icon to be displayed for this point
    var icon = {
        url: '/static/img/generated/' + row.image + ".png",
        anchor: new google.maps.Point(23, 25),
        scaledSize: new google.maps.Size(45, 45),
    }
    // where the point should be placed
    var point = new google.maps.LatLng(row.the_geom_plain[1], row.the_geom_plain[0]);
    var marker = new google.maps.Marker({
        position: point,
        map: map,
        title: row.description,
        icon: icon,
    })

    google.maps.event.addListener(marker, 'click', function(){
        infoWindow.setContent(generateBalloonText(row));
        infoWindow.open(map, marker);
    });

    marker.info = row

    return marker
}

function generateBalloonText(row){
    var s = ["<h4>Monitoring station at " + row.waterbody + "</h4>"];
    s.push("<strong>Status:</strong> " + row.status)
    s.push("<strong>Substrate:</strong> " + row.substrate_type)
    if(row.date_checked){
        s.push("<strong>Date Checked:</strong> " + row.date_checked);
    }
    if(row.description){
        s.push("<strong>Description:</strong> " + row.description);
    }

    s.push("<strong>Provider:</strong> " + row.agency);

    return s[0] + s.slice(1).join("<br />")
}
