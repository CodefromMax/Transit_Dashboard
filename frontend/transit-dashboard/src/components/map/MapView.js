import React from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';

const MapView = ({ center, zoom }) => {
  return (
    <MapContainer center={center} zoom={zoom} id="map">
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
    </MapContainer>
  );
};

export default MapView;