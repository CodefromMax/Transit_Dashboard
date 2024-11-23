import React from 'react';
import './Legend.css';

const GTFSLegend = ({ shapeColorMap }) => {
  return (
    <div className="legend legend-gtfs">
      <h4>GTFS Routes</h4>
      {Object.entries(shapeColorMap).map(([name, color]) => (
        <div key={name} className="legend-item">
          <i style={{ background: color }}></i>
          {name}
        </div>
      ))}
    </div>
  );
};

export default GTFSLegend;
