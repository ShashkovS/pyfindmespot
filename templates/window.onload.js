        window.onload = function () {
            function getJsonFromUrl() {
                var query = location.search.substr(1);
                var result = {};
                query.split("&").forEach(function (part) {
                    var item = part.split("=");
                    result[item[0]] = decodeURIComponent(item[1]);
                });
                return result;
            }
            // We’ll add a tile layer to add to our map, in this case it’s a OSM tile layer.
            // Creating a tile layer usually involves setting the URL template for the tile images
            var osmUrl = 'https://{s}.tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey=2996301b162b4c85910c10d2815529ce ',
                osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                osm = L.tileLayer(osmUrl, {
                    maxZoom: 18,
                    attribution: osmAttrib
                });
            var map = L.map('map').setView([0, 0], 2).addLayer(osm);
            function onEachFeature(feature, layer) {
                var popupContent = "<p></p>";
                if (feature.properties && feature.properties.Message) {
                    popupContent += feature.properties.Message;
                }
                layer.bindPopup(popupContent);
            }
            fetch("https://proj179.ru.ru/pyfindmespot/get_waypoints?trip_name=" + getJsonFromUrl().trip)
                .then((response) => {
                    return response.json();
                })
                .then((json) => {
                    for (var i of json.return.features) {
                        L.geoJSON(i, {onEachFeature: onEachFeature}).addTo(map);
                    }
                })
                .catch((err) => {
                    alert(err)
                })
        }
