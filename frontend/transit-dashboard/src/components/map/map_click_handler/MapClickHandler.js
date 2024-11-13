import React from 'react';
import { Marker, Polyline, useMapEvents, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import './MapClickHandler.css';

const MapClickHandler = ({ isEditMode, isEditDeleteMode, clickData, setClickData }) => {

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

  const deleteMarker = (id) => {
    setClickData((prevData) => {
  
      const updatedData = prevData.filter((data) => data.id !== id);
      return updatedData.map((data, index) => ({
        ...data,
        id: index + 1,
      }));
    });
  };

  const lineCoordinates = clickData.map((data) => [data.lat, data.lng]);

  useMapEvents({
    click: (e) => {
      if (isEditMode && !isEditDeleteMode) {
        const isStation = e.originalEvent.shiftKey;
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
          draggable={isEditDeleteMode}
          eventHandlers={{
            dragend: (e) => {
              if (isEditDeleteMode) {
                updateMarkerPosition(data.id, e.target.getLatLng());
              }
            },
            click: (e) => {
                if (isEditDeleteMode && e.originalEvent.shiftKey) {
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
