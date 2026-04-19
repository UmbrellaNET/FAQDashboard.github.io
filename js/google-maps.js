function initMap() {
    // Latitude and Longitude
    var myLatLng = {lat: -17.888429001768277, lng: 31.050776408553734};

    var map = new google.maps.Map(document.getElementById('google-maps'), {
        zoom: 17,
        center: myLatLng
    });

    var marker = new google.maps.Marker({
        position: myLatLng,
        map: map,
        title: 'Prospect, Waterfalls' // Title Location
    });
}