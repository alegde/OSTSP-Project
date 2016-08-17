// JavaScript source code
function initMap() {

    var directionsService = new google.maps.DirectionsService;
    var directionsDisplay = new google.maps.DirectionsRenderer({
        draggable: true,
        map: map,
        panel: document.getElementById('right-panel')
    });

    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 5,
        center: { lat: 37.09, lng: -100.71 }
    });

    var geocoder = new google.maps.Geocoder();

    directionsDisplay.setMap(map);

    var tour_data;

    $.ajax({
        'url': "http://localhost:8000/Data/Tour_Data.json",
        'async': false,
        'dataType': 'json',
        'success': function (data) {
            tour_data = data
        }
    });
    console.log(tour_data);
    tours = [];

    for (var i = 0; i < tour_data.features.length; i++) {
            tours.push({
                rating: tour_data.features[i].properties.rating,
                locations: tour_data.features[i].geometry.coordinates,
                names: tour_data.features[i].properties.buss_names,
                duration: tour_data.features[i].properties.duration,
                city_name: tour_data.features[i].properties.city,
                travel_mode: tour_data.features[i].properties.travel_type,
            });
    }


    document.getElementById("City").addEventListener('change', function () {
        geocodeAddress(geocoder, map);
        
    });

    document.getElementById('submit').addEventListener('click', function () {
        displayRoute(tours, directionsService, directionsDisplay);

    });
    console.log(tours)
}

function displayRoute(tours, service, display) {
    var travel_mode = document.getElementById("Travel_mode").value;
    var city_name = document.getElementById("City").value;
    points = []
    for (var i = 0; i < tours.length ; i++) {
        if (tours[i].city_name == city_name) {
            points.push(tours[i].locations)
        }
    }
    console.log(travel_mode);
    waypts = []
    for (var i = 1; i < (points[0].length - 1) ; i++) {
        waypts.push({
            location: { lat: points[0][i][0], lng: points[0][i][1] },
            stopover: true
        });
    }

    service.route({
        origin: { lat: points[0][0][0], lng: points[0][0][1] },
        destination: { lat: points[0][points[0].length - 1][0], lng: points[0][points[0].length - 1][1] },
        waypoints: waypts,
        optimizeWaypoints: true,
        travelMode: google.maps.TravelMode[travel_mode],
        avoidTolls: true
    }, function (response, status) {
        if (status === google.maps.DirectionsStatus.OK) {
            display.setDirections(response);
        } else {
            alert('Could not display directions due to: ' + status);
        }
    });
}

function geocodeAddress(geocoder, resultsMap) {
    var address = document.getElementById('City').value;
    geocoder.geocode({ 'address': address }, function (results, status) {
        if (status === google.maps.GeocoderStatus.OK) {
            resultsMap.setCenter(results[0].geometry.location);
            resultsMap.setZoom(10);
        } else {
            resultsMap.setCenter({ lat: 37.09, lng: -100.71 });
            resultsMap.setZoom(5);
        }
    });
}

