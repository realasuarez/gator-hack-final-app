import React from "react";

const TeacherNotesPanel = ({
  cls,
  value,
  onChange,
  onClear,
  onBack,
  rows = 6,
}) => {
  if (!cls) return null;
  return (
    <div className="panel notes-panel">
      <div className="notes-header">
        <div className="gradient-box">Teacher Notes</div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          {Boolean(value) && (
            <button className="add-notes-btn" onClick={onClear}>
              Clear Notes
            </button>
          )}
          {onBack && (
            <button className="add-notes-btn" onClick={onBack}>
              Back
            </button>
          )}
        </div>
      </div>
      <div className="notes-body">
        <textarea
          className="notes-input"
          placeholder={`Write notes for ${cls.code} — ${cls.name}...`}
          value={value || ""}
          onChange={(e) => onChange(e.target.value)}
          rows={rows}
        />
      </div>
    </div>
  );
};

export default TeacherNotesPanel;

