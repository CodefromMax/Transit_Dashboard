import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import CensusLayer from './components/layers/CensusLayer';
import GTFSLayer from './components/layers/GTFSLayer';
import CensusLegend from './components/legends/CensusLegend';
import GTFSLegend from './components/legends/GTFSLegend';
import LayerControlGroup from './components/controls/control_group/layer_control_group/LayerControlGroup';
import ModeToggle from './components/controls/toggle/mode_toggle/ModeToggle';
import ModeToggleControlGroup from './components/controls/control_group/mode_toggle_control_group/ModeToggleControlGroup';
import MapClickHandler from './components/map/map_click_handler/MapClickHandler';
import proj4 from 'proj4';
import StopsLayer from './components/layers/StopsLayer';
import CreateGTFSButton from './components/controls/button/create_gtfs_button/CreateGTFSButton';
import ClearAllButton from './components/controls/button/clear_all_button/ClearAllButton';

proj4.defs(
  'EPSG:3347',
  '+proj=lcc +lat_1=49 +lat_2=77 +lat_0=63.390675 +lon_0=-91.866667 +x_0=6200000 +y_0=3000000 +datum=NAD83 +units=m +no_defs'
);

const reprojectCoordinates = (coords) => {
  return coords.map(coord => {
    if (Array.isArray(coord[0])) {
      return reprojectCoordinates(coord);
    } else if (isFinite(coord[0]) && isFinite(coord[1])) {
      return proj4('EPSG:3347', 'EPSG:4326', coord);
    } else {
      console.error('Invalid coordinate pair:', coord);
      return coord;
    }
  });
};

const App = () => {
  const center = [43.5883, -79.3323];
  const zoom = 10;

  // This is the alignment data
  const [clickData, setClickData] = useState([]);

  // Edit or Edit + Delete Mode
  const [isEditMode, setIsEditMode] = useState(false);
  const [isEditDeleteMode, setIsEditDeleteMode] = useState(false);

  // State for toggling layers
  const [showCensusLayer, setShowCensusLayer] = useState(false);
  const [showGTFSLayer, setShowGTFSLayer] = useState(true);
  const [showStopsLayer, setShowStopsLayer] = useState(true);
  
  // State to store fetched data
  const [censusData, setCensusData] = useState(null);
  const [gtfsData, setGtfsData] = useState(null);
  const [stopsData, setStopsData] = useState(null);
  const [shapeColorMap, setShapeColorMap] = useState({});

  const controls_layers = [
    {
      label: 'Show Census Overlay',
      isChecked: showCensusLayer,
      onToggle: () => setShowCensusLayer(!showCensusLayer),
    },
    {
      label: 'Show GTFS Lines',
      isChecked: showGTFSLayer,
      onToggle: () => setShowGTFSLayer(!showGTFSLayer),
    },
    {
      label: 'Show Stops',
      isChecked: showStopsLayer,
      onToggle: () => setShowStopsLayer(!showStopsLayer),
    },
  ];
  
  const toggleMode = () => {
    setIsEditMode(!isEditMode);
    if (!isEditMode) {
      setIsEditDeleteMode(false); // Disable edit/delete when switching to view mode
    }
  };

  const toggleEditDeleteMode = () => {
    setIsEditDeleteMode(!isEditDeleteMode);
  };

  const clearAll = () => {
    setClickData([]);
  };

  const createGTFS = () => {
    if (clickData.length > 0) {
      console.log('Create GTFS with Alignment:', clickData);
    }
  };

  // Fetch Census data once
  useEffect(() => {
    fetch('/api/data/census/toronto_ct_boundaries_random_metric.geojson')
      .then(response => response.json())
      .then(data => {
        
        const reprojectedData = JSON.parse(JSON.stringify(data)); // Deep copy to avoid mutating original data
        reprojectedData.features.forEach((feature) => {
          if (feature.geometry.type === 'Polygon') {
            feature.geometry.coordinates = reprojectCoordinates(feature.geometry.coordinates);
          } else if (feature.geometry.type === 'MultiPolygon') {
            feature.geometry.coordinates = feature.geometry.coordinates.map((polygon) =>
              reprojectCoordinates(polygon)
            );
          }
        });
        setCensusData(reprojectedData); 
        console.log('Fetched Census')
      })
      .catch(error => console.error('Error loading Census GeoJSON:', error));
  }, []);

  // Fetch GTFS data once
  useEffect(() => {
    fetch('api/data/GTFS_data/gtfs_subway_lines.geojson')
      .then(response => response.json())
      .then(data => {
        setGtfsData(data); // Set fetched data
        console.log('Fetched GTFS')
        // Set a sample color map for GTFSLayer (can adjust logic as needed)
        const colors = ['#FF5733', '#33FF57', '#3357FF', '#FF33A6'];
        const map = data.features.reduce((acc, feature, index) => {
          acc[feature.properties.shape_id] = colors[index % colors.length];
          return acc;
        }, {});
        setShapeColorMap(map);
      })
      .catch(error => console.error('Error loading GTFS GeoJSON:', error));
  }, []);

  // Fetch GTFS data once
  useEffect(() => {
    fetch('api/data/GTFS_data/gtfs_subway_stops.geojson') // Update this URL if needed
      .then((response) => response.json())
      .then((data) => {
        console.log('Fetched Stops GeoJSON:', data); // Debug fetched data
        setStopsData(data);
      })
      .catch((error) => console.error('Error loading Stops GeoJSON:', error));
  }, []);

  
  return (
    <div style={{ position: 'relative' }}>
      <LayerControlGroup controls={controls_layers} />
      <ModeToggleControlGroup
        ModeToggle={
          <ModeToggle
            isEditMode={isEditMode}
            isEditDeleteMode={isEditDeleteMode}
            toggleMode={toggleMode}
            toggleEditDeleteMode={toggleEditDeleteMode}
          />
        }
        ClearAllButton={
          isEditDeleteMode && (
            <ClearAllButton onClear={clearAll} isDisabled={clickData.length === 0} />
          )
        }
        CreateGTFSButton={
          !isEditMode && (
            <CreateGTFSButton onCreate={createGTFS} isDisabled={clickData.length === 0} />
          )
        }
      />
      <MapContainer center={center} zoom={zoom} style={{ height: '100vh' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        {showCensusLayer && censusData && <CensusLayer data={censusData}/>}
        {showGTFSLayer && gtfsData && <GTFSLayer data={gtfsData} colorMap={shapeColorMap} />}
        {showStopsLayer && stopsData && <StopsLayer data={stopsData}/>}
        <MapClickHandler isEditMode={isEditMode} isEditDeleteMode={isEditDeleteMode} clickData={clickData} setClickData={setClickData}></MapClickHandler>
      </MapContainer>

      {showCensusLayer && censusData && <CensusLegend />}
      {showGTFSLayer && gtfsData && <GTFSLegend shapeColorMap={shapeColorMap} />}
    </div>
  );
};

export default App;
