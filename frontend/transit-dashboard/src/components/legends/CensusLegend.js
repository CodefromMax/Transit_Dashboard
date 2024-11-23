import React from 'react';
import './Legend.css';

const CensusLegend = () => {
  const grades = [0, 10, 20, 50, 100, 200, 500, 1000];
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

  return (
    <div className="legend legend-census">
      <h4>Census Density</h4>
      {grades.map((grade, index) => (
        <div key={index} className="legend-item">
          <i style={{ background: getColor(grade + 1) }}></i>
          {grade}{grades[index + 1] ? `–${grades[index + 1]}` : '+'}
        </div>
      ))}
    </div>
  );
};

export default CensusLegend;
