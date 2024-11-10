import React from 'react';

const ToggleLayerControl = ({ label, isChecked, onToggle }) => {
  return (
    <div className="toggle-layer-control">
      <label>
        <input
          type="checkbox"
          checked={isChecked}
          onChange={onToggle}
        />
        {label}
      </label>
    </div>
  );
};

export default ToggleLayerControl;
