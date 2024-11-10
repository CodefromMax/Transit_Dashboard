const z = 10
const x = 43.5883
const y = -79.3323

// Initialize the map and set the view to a specific location
let map = L.map('map').setView([x, y], z);
let geojson;
proj4.defs("EPSG:3347", "+proj=lcc +lat_1=49 +lat_2=77 +lat_0=63.390675 +lon_0=-91.866667 +x_0=6200000 +y_0=3000000 +datum=NAD83 +units=m +no_defs");

function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 5,
        color: '#666',
        dashArray: '',
        fillOpacity: 0.7
    });

    layer.bringToFront();
    info.update(layer.feature.properties);
}

function resetHighlight(e) {
    geojson.resetStyle(e.target);
    info.update();
}


function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: zoomToFeature
    });
}

function getColor(d) {
    return d > 1000 ? '#FFEDA0' :
           d > 500  ? '#FED976' :
           d > 200  ? '#FEB24C' :
           d > 100  ? '#FD8D3C' :
           d > 50   ? '#FC4E2A' :
           d > 20   ? '#E31A1C' :
           d > 10   ? '#BD0026' :
                      '#800026';
}

function style(feature) {
    return {
        fillColor: getColor(feature.properties.density),
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
    };
}

L.tileLayer(`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`, {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

var info = L.control();

info.onAdd = function(map) {
    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
    this.update();
    return this._div;
};

// method that we will use to update the control based on feature properties passed
info.update = function (props) {
    this._div.innerHTML = '<h4>Custom Metric for Census Tract</h4>' +  (props ?
        '<b>' + props.name + '</b><br />' + props.density
        : 'Hover over a census tract');
};

info.addTo(map);

var legend = L.control({position: 'bottomright'});

legend.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'),
        grades = [0, 10, 20, 50, 100, 200, 500, 1000],
        labels = [];

    // loop through our density intervals and generate a label with a colored square for each interval
    for (var i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +
            grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
    }

    return div;
};

legend.addTo(map);

fetch('http://localhost:8000/data/census/toronto_ct_boundaries_random_metric.geojson')
  .then(response => response.json())
  .then(data => {
    function reprojectCoordinates(coords) {
        return coords.map(coord => {
          // If the coordinate is a nested array (for rings in polygons), recurse into it
          if (Array.isArray(coord[0])) {
            return reprojectCoordinates(coord);
          } else if (isFinite(coord[0]) && isFinite(coord[1])) {
            // If the coordinate is a valid [x, y] pair, reproject it from EPSG:3347 to EPSG:4326
            return proj4('EPSG:3347', 'EPSG:4326', coord);
          } else {
            console.error('Invalid coordinate pair:', coord);
            return coord; // If invalid, return it as-is
          }
        });
      }
  
      // Loop through each feature in the GeoJSON and reproject its coordinates
      data.features.forEach(feature => {
        if (feature.geometry.type === "Polygon") {
          // Handle Polygon geometries
          feature.geometry.coordinates = reprojectCoordinates(feature.geometry.coordinates);
        } else if (feature.geometry.type === "MultiPolygon") {
          // Handle MultiPolygon geometries
          feature.geometry.coordinates = feature.geometry.coordinates.map(polygon => reprojectCoordinates(polygon));
        } else {
          console.warn(`Unsupported geometry type: ${feature.geometry.type}`);
        }
      });
    
      geojson = L.geoJson(data, {
        style: style,
        onEachFeature: onEachFeature
    }).addTo(map);

  })
  .catch(error => console.error('Error loading Census GeoJSON:', error))

fetch('http://localhost:8000/data/GTFS_data/gtfs_lines.geojson')
  .then(response => response.json())
  .then(data => {
      geojson = L.geoJson(data,{
        onEachFeature: onEachFeature
      }).addTo(map);
  })
  .catch(error => console.error('Error loading GTFS GeoJson:', error))

