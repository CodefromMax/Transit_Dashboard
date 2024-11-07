const z = 10
const x = 43.5883
const y = -79.3323

// Initialize the map and set the view to a specific location
let map = L.map('map').setView([x, y], z);
let geojson;
proj4.defs("EPSG:3347", "+proj=lcc +lat_1=49 +lat_2=77 +lat_0=63.390675 +lon_0=-91.866667 +x_0=6200000 +y_0=3000000 +datum=NAD83 +units=m +no_defs");

// function highlightFeature(e) {
//     var layer = e.target;

//     layer.setStyle({
//         weight: 5,
//         color: '#666',
//         dashArray: '',
//         fillOpacity: 0.7
//     });

//     layer.bringToFront();
//     info.update(layer.feature.properties);
// }

function highlightFeature(e) {
  // Only highlight when not in Create Mode
  if (!isCreateMode) {
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
  .catch(error => console.error('Error loading GeoJSON:', error))

//   // Function to add a marker at the clicked location
//   function onMapClick(e) {
//     // Show a confirmation dialog
//     const dropPin = confirm("Do you want to drop a pin here?");
    
//     // If the user confirms, add the pin
//     if (dropPin) {
//         const marker = L.marker(e.latlng).addTo(map);
        
//         // Optionally, add a popup to the marker
//         marker.bindPopup("You dropped a pin here!<br>Latitude: " + e.latlng.lat.toFixed(5) + "<br>Longitude: " + e.latlng.lng.toFixed(5)).openPopup();
//     }
// }

// // Attach the click event to the map to call onMapClick when the map is clicked
// map.on('click', onMapClick);


// Mode toggle checkbox
const modeToggle = document.getElementById('modeToggle');

// Variable to store the current mode
let isCreateMode = false; // Default mode is "View Mode"

// Switch mode when checkbox is toggled
modeToggle.onchange = function() {
    isCreateMode = !isCreateMode;  // Toggle the mode
    if (isCreateMode) {
        modeToggle.nextElementSibling.textContent = "Create Mode"; // Update label to "Create Mode"
    } else {
        modeToggle.nextElementSibling.textContent = "Create Mode"; // Update label to "View Mode"
    }
};



// Reference to the overlay dialog and buttons
const overlayConfirm = document.getElementById('overlayConfirm');
const overlayYes = document.getElementById('overlayYes');
const overlayNo = document.getElementById('overlayNo');

// Function to add a marker after user confirms
function addMarker(latlng) {
    const marker = L.marker(latlng).addTo(map);
    marker.bindPopup("You dropped a pin here!<br>Latitude: " + latlng.lat.toFixed(5) + "<br>Longitude: " + latlng.lng.toFixed(5)).openPopup();
}

// Function to handle the map click and show the overlay dialog
function onMapClick(e) {
    console.log("Map clicked, showing confirm dialog."); // Log click event
    
    const { latlng, originalEvent } = e;
    
    // Check if the event contains page coordinates
    if (originalEvent && originalEvent.pageX && originalEvent.pageY) {
        // Set overlay position based on the cursor coordinates
        overlayConfirm.style.left = originalEvent.pageX + 'px';
        overlayConfirm.style.top = originalEvent.pageY + 'px';
        console.log("Position set to:", originalEvent.pageX, originalEvent.pageY); // Log coordinates
    } else {
        console.error("originalEvent is missing page coordinates.");
    }
    
    // Show the overlay dialog
    overlayConfirm.style.display = 'block';

    map.dragging.disable();
    map.scrollWheelZoom.disable();
    map.doubleClickZoom.disable();
    map.boxZoom.disable();
    map.keyboard.disable();

    // Clear any previous click handlers to avoid duplicates
    overlayYes.onclick = overlayNo.onclick = null;

    // Handle the "Yes" button click to add marker
    overlayYes.onclick = function() {
        console.log("User confirmed pin drop.");
        addMarker(latlng);
        overlayConfirm.style.display = 'none'; // Hide the dialog
    };

    // Handle the "No" button click to simply hide the dialog
    overlayNo.onclick = function() {
        console.log("User canceled pin drop.");
        overlayConfirm.style.display = 'none';
    };
}

function reEnableMapInteractions() {
  map.dragging.enable();
  map.scrollWheelZoom.enable();
  map.doubleClickZoom.enable();
  map.boxZoom.enable();
  map.keyboard.enable();
}

// Attach the click event to the map
map.on('click', onMapClick);





// // Simulated GTFS stop data
// const stops = [
//     { stop_id: '1', stop_name: 'Station 1', stop_lat: 51.505, stop_lon: -0.09 },
//     { stop_id: '2', stop_name: 'Station 2', stop_lat: 51.51, stop_lon: -0.1 }
// ];

// // Function to load and display GTFS stops on the map
// function loadStops(stops) {
//     stops.forEach(stop => {
//         L.marker([stop.stop_lat, stop.stop_lon])
//             .addTo(map)
//             .bindPopup(stop.stop_name);
//     });
// // }

// // Load the initial stops from the simulated GTFS data
// loadStops(stops);

// // Click event to allow adding new stops interactively
// map.on('click', function (e) {
//     // Get the latitude and longitude of the click event
//     const newStopLat = e.latlng.lat;
//     const newStopLon = e.latlng.lng;

//     // Prompt the user to enter a stop name
//     const stopName = prompt('Enter stop name for the new station:');
//     if (stopName) {
//         // Add new stop marker to the map
//         const newMarker = L.marker([newStopLat, newStopLon])
//             .addTo(map)
//             .bindPopup(stopName);

//         // Optionally, simulate adding the new stop to the GTFS data (client-side only for now)
//         const newStop = {
//             stop_id: Math.random().toString(36).substring(2, 15), // Generate a random stop ID
//             stop_name: stopName,
//             stop_lat: newStopLat,
//             stop_lon: newStopLon
//         };

//         // Add the new stop to the list of stops (for simulation purposes)
//         stops.push(newStop);

//         console.log('New stop added:', newStop);
//     }
// });
