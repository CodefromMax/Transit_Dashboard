import React from 'react';
import { GeoJSON } from 'react-leaflet';
import L from 'leaflet';

const StopsLayer = ({ data }) => {
  // Style for the points
  const style = {
    color: '#000000', // Orange-red color for the stops
    weight: 0.5,
    opacity: 0.5,
    fillColor: '#000000',
    fillOpacity: 0.8,
    radius: 2, // Size of the circle markers
  };

  // Function to convert points to circle markers and bind popups
  const pointToLayer = (feature, latlng) => {
    return L.circleMarker(latlng, style).bindPopup(`<b>${feature.properties.stop_name}</b>`);
  };

  return (
    <GeoJSON
      data={data}
      pointToLayer={pointToLayer} // Render points as circle markers
    />
  );
};

export default StopsLayer;
