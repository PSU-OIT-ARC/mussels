var map = null;
var markers = [];
var infoWindow = null;
var clusters = {}
var xhr = null;
var loading_bar_time_id = null;

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
    map.controls[google.maps.ControlPosition.RIGHT_TOP].push(document.getElementById("search-button"))

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

    // add the events for the search and apply buttons
    $('#apply-button').click(applyClick)
    $('#search-button').click(showSearch);

    // fetch all the markers, then render them
    fetchMarkers(renderMarkers, {});
});

function showSearch(){
    // show the search forms, and register events that trigger it to be closed
    $('#overlay, #search').show()
    $('#overlay').click(hideSearch);
    $(window).keyup(function(e){
        if(e.keyCode == 27){ // esc key
            hideSearch();
        }
    });
}

function hideSearch(){
    // hide the search form, and unbind all the events that showSearch setup
    $('#overlay, #search').hide()
    $('#overlay').unbind('click');
    $(window).unbind('keyup');
}

function startLoading(){
    // start rendering the loading bar
    var states = " . .. ... .... .....".split(" ");

    loading_bar_time_id = setInterval(function loading(){
        var old_state = states.shift();
        states.push(old_state);
        $('#progress').html(old_state);
        return loading;
    }(), 250);

    $('#overlay, #loading').show();
}

function stopLoading(){
    // stop rendering the loading bar
    $('#overlay, #loading').hide();
    clearInterval(loading_bar_time_id);
}

function buildKwargs(){
    // generate the search parameters based on the input from the form
    var kwargs = {}
    var species = ['lame'] // jQuery won't create a querystring with an empty array, so we add something to it
    $('.specie-checkbox:checked').each(function(){
        species.push($(this).val());
    });
    kwargs['species'] = species;

    var substrates = ['lame']
    $('.substrate-checkbox:checked').each(function(){
        substrates.push($(this).val());
    });
    kwargs['substrates'] = substrates

    var waterbody = $('#waterbody').val();
    if($.trim(waterbody) != ""){
        kwargs['waterbody'] = waterbody;
    }

    var agency = $('#agency').val();
    if($.trim(agency) != ""){
        kwargs['agency'] = agency;
    }

    return kwargs;
}

function applyClick(){
    // when search criteria is entered, clear everything on the map
    clear()
    hideSearch();
    var kwargs = buildKwargs();

    // fetch all the markers and render them
    fetchMarkers(renderMarkers, kwargs)
}

function clear(){
    // clear all the markers and clusters on the map
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
    // fetch the markers from the server
    if(xhr) xhr.abort();
    startLoading();
    xhr = $.getJSON("/json", kwargs, function(data){
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
    // this groups the markers by the specie associated with the marker
    var markers_grouped_by_specie = {}
    for(var i = 0; i < markers.length; i++){
        var marker = markers[i];
        // init the array inside the cluster
        if(!(marker.info.specie_key in markers_grouped_by_specie)){
            markers_grouped_by_specie[marker.info.specie_key] = []
        }

        // add this marker to the right cluster
        markers_grouped_by_specie[marker.info.specie_key].push(marker);
    }

    // now draw all the clusters on the map
    drawClustersBySpecie(markers_grouped_by_specie, Object.keys(markers_grouped_by_specie))

    // hide the loading bar since everything is loaded now
    stopLoading();
}

// draws a set of clusters on the map
function drawClustersBySpecie(groups, keys){
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
        map: null,
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
    s.push("<strong>Specie:</strong> " + row.specie)
    s.push("<strong>Substrate:</strong> " + row.substrates)
    if(row.date_checked){
        s.push("<strong>Date Checked:</strong> " + row.date_checked);
    }
    if(row.description){
        s.push("<strong>Description:</strong> " + row.description);
    }

    s.push("<strong>Provider:</strong> " + row.agency);

    return s[0] + s.slice(1).join("<br />")
}
