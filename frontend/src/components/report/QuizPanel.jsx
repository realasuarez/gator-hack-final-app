import React from "react";

const QuizPanel = ({ classes, selectedIds, onToggle, onGenerate }) => {
  return (
    <div className="panel quiz-panel">
      <div className="gradient-box">Practice Questions</div>
      <div className="quiz-list">
        {classes.map((c) => {
          const checked = selectedIds.includes(c.id);
          return (
            <label key={c.id} className={`quiz-item ${checked ? "checked" : ""}`}>
              <input
                type="checkbox"
                checked={checked}
                onChange={(e) => onToggle(c.id, e.target.checked)}
              />
              <span className="quiz-item-text">
                <strong>{c.code}</strong> — {c.name}
              </span>
            </label>
          );
        })}
      </div>
      {selectedIds.length > 0 && (
        <div className="generate-row">
          <button className="generate-btn" onClick={() => onGenerate(selectedIds)}>
            Generate Questions
          </button>
        </div>
      )}
    </div>
  );
};

export default QuizPanel;

