import React from 'react';
import './CreateGTFSButton.css';

const CreateGTFSButton = ({ onCreate, isDisabled }) => {
  return (
    <button
      onClick={onCreate}
      disabled={isDisabled}
      className={`control-button ${isDisabled ? 'disabled' : ''}`}
    >
      Create GTFS
    </button>
  );
};

export default CreateGTFSButton;
