import React from 'react';
import './ClearAllButton.css';

const ClearAllButton = ({ onClear, isDisabled }) => {
  return (
    <button
      onClick={onClear}
      disabled={isDisabled}
      className={`control-button ${isDisabled ? 'disabled' : ''}`}
    >
      Clear Alignmnent
    </button>
  );
};

export default ClearAllButton;
