import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';
import './ModeToggleControlGroup.css';

const ModeToggleControlGroup = ({ ModeToggle, ClearAllButton, CreateGTFSButton }) => {
  return (
    <Card className="mode-toggle-control-group">
      <CardContent>
        <Typography variant="h6">Mode Controls</Typography>
        <div className="mode-toggle-item">{ModeToggle}</div>
        {ClearAllButton && <div className="control-button-wrapper">{ClearAllButton}</div>}
        {CreateGTFSButton && <div className="control-button-wrapper">{CreateGTFSButton}</div>}
      </CardContent>
    </Card>
  );
};

export default ModeToggleControlGroup;
