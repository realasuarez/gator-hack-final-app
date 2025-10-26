import React from "react";
import ClassSummary from "../ClassSummary";

const SummaryPanel = ({ cls, onBack }) => {
  if (!cls) return null;
  return (
    <div className="summary-panel">
      <div className="summary-header">
        <ClassSummary cls={cls} />
        {onBack && (
          <button className="close-summary" onClick={onBack}>
            Back
          </button>
        )}
      </div>
    </div>
  );
};

export default SummaryPanel;

