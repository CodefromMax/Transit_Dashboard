import React from 'react';
import { FormControlLabel, Switch } from '@mui/material';
import './ModeToggle.css';

const ModeToggle = ({ isEditMode, isEditDeleteMode, toggleMode, toggleEditDeleteMode }) => {
  return (
    <div className="toggle-layer-control-">
      <FormControlLabel
        control={<Switch checked={isEditMode} onChange={toggleMode} />}
        label={isEditMode ? 'Draw Mode' : 'View Mode'}
      />
      {isEditMode && (
        <FormControlLabel
          control={<Switch checked={isEditDeleteMode} onChange={toggleEditDeleteMode} />}
          label={isEditDeleteMode ? "Disable Edit/Delete" :  "Enable Edit/Delete"}
        />
      )}
    </div>
  );
};

export default ModeToggle;
