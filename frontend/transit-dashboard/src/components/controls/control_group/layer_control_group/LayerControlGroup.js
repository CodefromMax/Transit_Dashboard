import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';
import ToggleLayerControl from '../../toggle/layer_control_toggle/LayerControlToggle';
import './LayerControlGroup.css';

const LayerControlGroup = ({ controls }) => {
  return (
    <Card className="layer-control-group">
      <CardContent>
        <Typography variant="h6">Layer Controls</Typography>
        {controls.map(({ label, isChecked, onToggle }) => (
          <ToggleLayerControl
            key={label}
            label={label}
            isChecked={isChecked}
            onToggle={onToggle}
          />
        ))}
      </CardContent>
    </Card>
  );
};

export default LayerControlGroup;
