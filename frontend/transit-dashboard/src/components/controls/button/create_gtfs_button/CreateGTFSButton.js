import React from 'react';
import './CreateGTFSButton.css';

const CreateGTFSButton = ({ onCreate, isDisabled }) => {
  return (
    <button
      onClick={onCreate}
      disabled={isDisabled}
      className={`control-button ${isDisabled ? 'disabled' : ''}`}
    >
      Calculate Metrics
    </button>
  );
};

export default CreateGTFSButton;
