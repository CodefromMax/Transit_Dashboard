import React, { useState } from 'react';
import { Marker, Polyline, useMapEvents, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import './MapClickHandler.css';

const MapClickHandler = ({ isEditMode, isEditDeleteMode }) => {
  const [clickData, setClickData] = useState([]);

  // Add a new marker
  const addMarker = (latlng, type) => {
    setClickData((prevData) => [
      ...prevData,
      {
        id: prevData.length + 1,
        type,
        lat: latlng.lat,
        lng: latlng.lng,
      },
    ]);
  };

  // Update marker position
  const updateMarkerPosition = (id, latlng) => {
    setClickData((prevData) =>
      prevData.map((data) =>
        data.id === id
          ? {
              ...data,
              lat: latlng.lat,
              lng: latlng.lng,
            }
          : data
      )
    );
  };

  // Delete a marker
  const deleteMarker = (id) => {
    setClickData((prevData) => {
      // Filter out the marker to be deleted
      const updatedData = prevData.filter((data) => data.id !== id);

      // Reassign IDs dynamically based on the new order
      return updatedData.map((data, index) => ({
        ...data,
        id: index + 1, // Reassign sequential IDs
      }));
    });
  };

  const lineCoordinates = clickData.map((data) => [data.lat, data.lng]);

  // Map event handlers
  useMapEvents({
    click: (e) => {
      if (isEditMode && !isEditDeleteMode) {
        // Single click in edit mode to add markers
        const isStation = e.originalEvent.shiftKey; // Use Shift key for stations
        addMarker(e.latlng, isStation ? 'station' : 'waypoint');
      }
    },
  });

  return (
    <>
    <Polyline positions={lineCoordinates} color="blue" />

      {clickData.map((data) => (
        <Marker
          key={data.id}
          position={[data.lat, data.lng]}
          draggable={isEditDeleteMode} // Enable dragging in delete mode
          eventHandlers={{
            dragend: (e) => {
              if (isEditDeleteMode) {
                updateMarkerPosition(data.id, e.target.getLatLng());
              }
            },
            click: (e) => {
                if (isEditDeleteMode && e.originalEvent.shiftKey) {
                  // Shift + Click to delete the marker
                  deleteMarker(data.id);
                }
            },
          }}
          icon={L.divIcon({
            className: `marker-icon ${data.type}`,
            html: `<div style="background-color: ${
              data.type === 'station' ? 'red' : 'black'
            }; width: 10px; height: 10px; border-radius: 50%;"></div>`,
          })}
        >
          <Tooltip>{`Type: ${data.type}, ID: ${data.id}`}</Tooltip>
        </Marker>
      ))}
    </>
  );
};

export default MapClickHandler;
