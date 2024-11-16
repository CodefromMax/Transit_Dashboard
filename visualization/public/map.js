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
    if (!isCreateMode) {
        map.fitBounds(e.target.getBounds());
    }
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
        map.doubleClickZoom.disable();
        map.boxZoom.disable();
        console.log("[Toggle]: Create Mode")
    } else {
        modeToggle.nextElementSibling.textContent = "Create Mode"; // Update label to "View Mode"
        map.doubleClickZoom.enable();
        map.boxZoom.enable();
        console.log("[Toggle]: View Mode")
    }
};


// function parseQuery(query) {
//   const parts = query.split(/\s+/); // Split by whitespace
//   if (parts.length === 1) {
//       return parts[0]; // Single street or place
//   } else if (parts.length === 2) {
//       return `${parts[0]} & ${parts[1]}`; // Assume intersection
//   } else {
//       return query; // Full query as-is for more complex search
//   }
// }

// document.getElementById('searchButton').addEventListener('click', function() {
//   const query = document.getElementById('searchInput').value;

//   if (query) {
//       const formattedQuery = parseQuery(query);
//       fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(formattedQuery)}&format=json&addressdetails=1`)
//           .then(response => response.json())
//           .then(data => {
//               if (data && data.length > 0) {
//                   const firstResult = data[0];
//                   const lat = parseFloat(firstResult.lat);
//                   const lon = parseFloat(firstResult.lon);

//                   // Move the map to the result location
//                   map.setView([lat, lon], 15); 

//                   highlightedLayer = L.circle([lat, lon], {
//                     color: 'blue',       // Color of the circle border
//                     fillColor: 'blue',   // Fill color inside the circle
//                     fillOpacity: 0.4,   // Transparency of the fill
//                     radius: 100         // Radius of the circle (in meters)
//                     }).addTo(map);

//                   // // Add a marker to the map for the result
//                   // L.marker([lat, lon]).addTo(map)
//                   //   .bindPopup(`Search Result: ${firstResult.display_name}`)
//                   //   .openPopup();
//               } else {
//                   alert('No results found for this query. Try a different location or intersection.');
//               }
//           })
//           .catch(error => {
//               console.error('Error during search:', error);
//               alert('Error fetching search results.');
//           });
//   }
// });

let highlightedLayer = null;  // To store the highlighted layer

document.getElementById('searchButton').addEventListener('click', function() {
    const query = document.getElementById('searchInput').value.trim();

    if (query) {
        const formattedQuery = parseQuery(query);
        fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(formattedQuery)}, Toronto&format=json&addressdetails=1`)
            .then(response => response.json())
            .then(data => {
                if (data && data.length > 0) {
                    handleSearchResults(data, query);  // Pass the query to identify intersection or location
                } else {
                    alert('No results found. Try being more specific.');
                }
            })
            .catch(error => {
                console.error('Search failed:', error);
                alert('Error fetching search results.');
            });
    }
});

const streetSuffixes = {
  'st': 'Street',
  'ave': 'Avenue',
  'rd': 'Road',
  'blvd': 'Boulevard',
  'dr': 'Drive',
  'cres': 'Crescent',
  'pt': 'Parkway',
  'sq': 'Square',
  'hwy': 'Highway'
};

// This function determines if the query is a street intersection or a location
function parseQuery(query) {
  const parts = query.split(/\s+/); // Split by whitespace
  if (parts.length === 1) {
      return parts[0]; // Single street or place
  } else if (parts.length === 2) {
      return `${parts[0]} & ${parts[1]}`; // Assume intersection
  }else if (query.includes(' and ') || query.includes(' & ') || query.includes(' at ')) {
      const intersection = query.toLowerCase().split(" and ");
      return `${intersection[0]} & ${intersection[1]}`;
  } else {
      return query; // Full query as-is for more complex search
  }
}
// function parseQuery(query) {
//     // Check if the query seems like an intersection (two street names, separated by 'and' or '&')
//     if (query.includes(' and ') || query.includes(' & ') || query.includes(' at ')) {
//         return query; // It is likely an intersection
//     }
//     return query; // Otherwise treat it as a location
// }

// Handle search results and highlight the correct feature
function handleSearchResults(results, query) {
    const topResult = results[0];
    const lat = parseFloat(topResult.lat);
    const lon = parseFloat(topResult.lon);

    // Move map to the location
    map.setView([lat, lon], 15);

    // Remove previous highlighted layer (if any)
    if (highlightedLayer) {
        map.removeLayer(highlightedLayer);
    }

    // Determine if the query was an intersection or a location
    if (query.includes(' and ') || query.includes(' & ') || query.includes(' at ')) {
        highlightStreetIntersection(query, lat, lon);  // Highlight the street intersection
    } else {
        highlightLocation(lat, lon, topResult.display_name);  // Highlight the location (e.g., landmark)
    }
}

// Highlight the street intersection (using a circle or custom marker)
function highlightStreetIntersection(query, lat, lon) {
    highlightedLayer = L.circle([lat, lon], {
        color: 'blue',
        fillColor: 'blue',
        fillOpacity: 0.4,
        radius: 100
    }).addTo(map);

    const label = L.divIcon({
        className: 'bold-label',
        html: `<div style="font-weight: bold; color: blue; font-size: 16px;">Intersection: ${query}</div>`,
        iconSize: [200, 30]
    });

    // // Add the label to the map at the intersection location
    // L.marker([lat, lon], { icon: label }).addTo(map);

    // // Add a marker for the intersection with a popup
    // L.marker([lat, lon]).addTo(map)
    //     .bindPopup(`Intersection: <br><b>${query}</b>`)
    //     .openPopup();
}

// Highlight the location (e.g., landmark or neighborhood)
function highlightLocation(lat, lon, locationName) {
    highlightedLayer = L.circle([lat, lon], {
        color: 'green',
        fillColor: 'green',
        fillOpacity: 0.4,
        radius: 100
    }).addTo(map);

    const label = L.divIcon({
        className: 'bold-label',
        html: `<div style="font-weight: bold; color: green; font-size: 16px;">Location: ${locationName}</div>`,
        iconSize: [200, 30]
    });

    // // Add the label to the map at the location
    // L.marker([lat, lon], { icon: label }).addTo(map);

    // // Add a marker for the location with a popup
    // L.marker([lat, lon]).addTo(map)
    //     .bindPopup(`Location: <br><b>${locationName}</b>`)
    //     .openPopup();
}


// Reference to the overlay dialog and buttons
const overlayConfirm = document.getElementById('overlayConfirm');
const overlayYes = document.getElementById('overlayYes');
const overlayNo = document.getElementById('overlayNo');
let pinCounter = 0;

// Function to add a marker and display the closest road type along with latitude and longitude
function addMarker(latlng) {
  // Reverse geocoding to get the closest road/area
  const apiUrl = `https://nominatim.openstreetmap.org/reverse?lat=${latlng.lat}&lon=${latlng.lng}&format=json&addressdetails=1`;

  fetch(apiUrl)
      .then(response => response.json())
      .then(data => {
          // Get the closest road/area name from the returned data
          const road = data.address.road || data.address.avenue || data.address.boulevard ||
              data.address.footway || data.address.path || data.address.pedestrian ||
              data.address.highway || "Unknown Road"; // Fallback to "Unknown Road" if no suitable road is found

          // Create the marker and bind a popup with latitude, longitude, and the closest road type
          const marker = L.marker(latlng).addTo(map);
          pinCounter++;
          marker.bindPopup(`
              You dropped a pin here!<br>
              Latitude: ${latlng.lat.toFixed(5)}<br>
              Longitude: ${latlng.lng.toFixed(5)}<br>
              Closest Road: ${road}<br>
              Number of Station (s): ${pinCounter}
          `).openPopup();

          // Handle the click event for the marker
          marker.on('click', function() {
              if (confirm("Do you want to remove this pin?")) {
                  map.removeLayer(marker); // Remove marker from the map
                  pinCounter --;
              }
          });
      })
      .catch(error => {
          console.error('Error getting the closest road:', error);
          // If there's an error, still add the marker but without the road info
          const marker = L.marker(latlng).addTo(map);
          marker.bindPopup(`
              You dropped a pin here!<br>
              Latitude: ${latlng.lat.toFixed(5)}<br>
              Longitude: ${latlng.lng.toFixed(5)}<br>
              Closest Road: Unknown
          `).openPopup();
      });
}

// Function to handle the map click and show the overlay dialog
function onMapClick(e) {
  if (isCreateMode) {
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
      overlayYes.onclick = function () {
          console.log("User confirmed pin drop.");
          addMarker(latlng); // Add the marker with closest road information
          overlayConfirm.style.display = 'none'; // Hide the dialog
          reEnableMapInteractions();
      };

      // Handle the "No" button click to simply hide the dialog
      overlayNo.onclick = function () {
          console.log("User canceled pin drop.");
          overlayConfirm.style.display = 'none';
          reEnableMapInteractions();
      };
  }
}


// // Function to add a marker after user confirms
// function addMarker(latlng) {
//     const marker = L.marker(latlng).addTo(map);
//     marker.bindPopup("You dropped a pin here!<br>Latitude: " + latlng.lat.toFixed(5) + "<br>Longitude: " + latlng.lng.toFixed(5)).openPopup();
//     marker.on('click', function() {
//       if (confirm("Do you want to remove this pin?")) {
//           map.removeLayer(marker); // Remove marker from the map
//       }
//   });
// }

// // Function to handle the map click and show the overlay dialog
// function onMapClick(e) {
//     if(isCreateMode){
//         console.log("Map clicked, showing confirm dialog."); // Log click event
        
//         const { latlng, originalEvent } = e;
        
//         // Check if the event contains page coordinates
//         if (originalEvent && originalEvent.pageX && originalEvent.pageY) {
//             // Set overlay position based on the cursor coordinates
//             overlayConfirm.style.left = originalEvent.pageX + 'px';
//             overlayConfirm.style.top = originalEvent.pageY + 'px';
//             console.log("Position set to:", originalEvent.pageX, originalEvent.pageY); // Log coordinates
//         } else {
//             console.error("originalEvent is missing page coordinates.");
//         }
        
//         // Show the overlay dialog
//         overlayConfirm.style.display = 'block';

//         map.dragging.disable();
//         map.scrollWheelZoom.disable();
//         map.doubleClickZoom.disable();
//         map.boxZoom.disable();
//         map.keyboard.disable();

//         // Clear any previous click handlers to avoid duplicates
//         overlayYes.onclick = overlayNo.onclick = null;

//         // Handle the "Yes" button click to add marker
//         overlayYes.onclick = function() {
//             console.log("User confirmed pin drop.");
//             addMarker(latlng);
//             overlayConfirm.style.display = 'none'; // Hide the dialog
//             reEnableMapInteractions()
//         };

//         // Handle the "No" button click to simply hide the dialog
//         overlayNo.onclick = function() {
//             console.log("User canceled pin drop.");
//             overlayConfirm.style.display = 'none';
//             reEnableMapInteractions()
//         };
        
//     }

// }

function reEnableMapInteractions() {
  map.dragging.enable();
  map.scrollWheelZoom.enable();
  // map.doubleClickZoom.enable();
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
