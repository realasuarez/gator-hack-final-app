import React from "react";

const ClassesPanel = ({
  classes,
  noteMode,
  onToggleNoteMode,
  onSelectForNotes,
  onSelectForSummary,
  notesByClass,
}) => {
  return (
    <div className="class-list-panel">
      <div className="class-list-header">
        <div className="gradient-box">Your Classes</div>
        <div className="notes-toolbar">
          {noteMode && <span className="select-hint">Select a class to add notes</span>}
          <button
            className={`add-notes-btn ${noteMode ? "active" : ""}`}
            onClick={onToggleNoteMode}
          >
            {noteMode ? "Cancel" : "Add Notes"}
          </button>
        </div>
      </div>

      <table className={`classes-table ${noteMode ? "note-mode" : ""}`}>
        <thead>
          <tr>
            <th>Course</th>
            <th>Term</th>
            <th>Students</th>
          </tr>
        </thead>
        <tbody>
          {classes.map((c) => (
            <tr
              key={c.id}
              onClick={() => (noteMode ? onSelectForNotes(c) : onSelectForSummary(c))}
            >
              <td>
                <strong>{c.code}</strong> — {c.name}
                {notesByClass[c.id] && (
                  <span className="notes-indicator" title="Notes saved">📝</span>
                )}
              </td>
              <td>{c.term}</td>
              <td>{c.students}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ClassesPanel;

