import React from 'react';
import { FormControlLabel, Switch } from '@mui/material';
import './LayerControlToggle.css';

const LayerControlToggle = ({ label, isChecked, onToggle }) => {
  return (
    <div className="toggle-layer-control">
      <FormControlLabel
        control={<Switch checked={isChecked} onChange={onToggle} />}
        label={label}
      />
    </div>
  );
};

export default LayerControlToggle;

