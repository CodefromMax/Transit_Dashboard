import React from 'react';
import { GeoJSON } from 'react-leaflet';

// Style function for GTFS lines using the colorMap prop
const gtfsStyle = (feature, colorMap) => ({
  color: colorMap[feature.properties.name],
  weight: 5,
  opacity: 1
});

const onEachFeature = (feature, layer) => {
  if (feature.properties && feature.properties.name) {
    // Bind a popup to each line with its shape_id
    layer.bindPopup(`${feature.properties.name}`);
    // // Optionally add a click event for additional interactivity
    // layer.on('click', () => {
    //   console.log(`Clicked on line: ${feature.properties.name}`);
    // });
  }
};

const GTFSLayer = ({ data, colorMap }) => {
  return (
    <GeoJSON
      data={data}
      style={(feature) => gtfsStyle(feature, colorMap)}
      onEachFeature={onEachFeature} // Attach event handlers
    />
  );
};

export default GTFSLayer;
