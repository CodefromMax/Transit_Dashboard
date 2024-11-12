import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';
import './ModeToggleControlGroup.css';

const ModeToggleControlGroup = ({ ModeToggle }) => {
  return (
    <Card className="mode-toggle-control-group">
      <CardContent>
        <Typography variant="h6">Mode Controls</Typography>
        <div className="mode-toggle-item">{ModeToggle}</div>
      </CardContent>
    </Card>
  );
};

export default ModeToggleControlGroup;
