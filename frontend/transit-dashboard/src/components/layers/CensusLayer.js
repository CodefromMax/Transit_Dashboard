import React from 'react';
import { GeoJSON } from 'react-leaflet';

const getColor = (density) => {
  return density > 1000 ? '#FFEDA0' :
         density > 500  ? '#FED976' :
         density > 200  ? '#FEB24C' :
         density > 100  ? '#FD8D3C' :
         density > 50   ? '#FC4E2A' :
         density > 20   ? '#E31A1C' :
         density > 10   ? '#BD0026' :
                          '#800026';
};

const style = (feature) => ({
  fillColor: getColor(feature.properties.density),
  weight: 1,
  opacity: 0.7,
  color: 'white',
  dashArray: '5',
  fillOpacity: 0.5
});

const CensusLayer = React.memo(({ data }) => {
    return <GeoJSON data={data} style={style} />;
});

export default CensusLayer;
