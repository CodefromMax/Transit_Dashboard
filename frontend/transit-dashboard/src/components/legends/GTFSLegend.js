import React from 'react';
import './Legend.css';

const GTFSLegend = ({ shapeColorMap }) => {
  return (
    <div className="legend legend-gtfs">
      <h4>GTFS Routes</h4>
      {Object.entries(shapeColorMap).map(([shape_id, color]) => (
        <div key={shape_id} className="legend-item">
          <i style={{ background: color }}></i>
          {shape_id}
        </div>
      ))}
    </div>
  );
};

export default GTFSLegend;
