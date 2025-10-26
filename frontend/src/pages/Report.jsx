import React, { useEffect, useState } from "react";
import "./Report.css";
import ClassesPanel from "../components/report/ClassesPanel";
import SummaryPanel from "../components/report/SummaryPanel";
import QuizPanel from "../components/report/QuizPanel";
import TeacherNotesPanel from "../components/report/TeacherNotesPanel";

function Report() {
  const [selectedClass, setSelectedClass] = useState(null);
  const [noteMode, setNoteMode] = useState(false);
  const [notesByClass, setNotesByClass] = useState({});
  const [selectedForQuiz, setSelectedForQuiz] = useState([]);
  const [viewMode, setViewMode] = useState(null); // 'summary' | 'notes' | null

  // Load and persist notes in localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem("classNotes");
      if (saved) setNotesByClass(JSON.parse(saved));
    } catch {}
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem("classNotes", JSON.stringify(notesByClass));
    } catch {}
  }, [notesByClass]);

  const classes = [
    { id: 1, name: "Intro to CS", code: "COP 3502", term: "Fall 2025", students: 120 },
    { id: 2, name: "Data Structures", code: "COP 3530", term: "Fall 2025", students: 95 },
    { id: 3, name: "Algorithms", code: "CIS 4930", term: "Spring 2026", students: 80 },
    { id: 4, name: "Software Engineering", code: "CEN 3031", term: "Spring 2026", students: 110 },
  ];

  return (
    <div className="report">
      <header className="dashboard-header">
        <button className="back-button" onClick={() => (window.location.href = "/")}>
          Back
        </button>
        <h1 className="dashboard-title">Report</h1>
      </header>

      <div className={`report-container ${selectedClass ? "show-summary" : ""}`}>
        {/* Classes Panel */}
        <ClassesPanel
          classes={classes}
          noteMode={noteMode}
          onToggleNoteMode={() => setNoteMode((v) => !v)}
          notesByClass={notesByClass}
          onSelectForNotes={(c) => {
            setSelectedClass(c);
            setViewMode("notes");
            setNoteMode(false);
          }}
          onSelectForSummary={(c) => {
            if (selectedClass?.id === c.id) {
              setSelectedClass(null);
              setViewMode(null);
            } else {
              setSelectedClass(c);
              setViewMode("summary");
            }
          }}
        />

        {/* Right column: summary and actions */}
        {selectedClass && viewMode === "summary" && (
          <div className="right-column">
            <SummaryPanel
              cls={selectedClass}
              onBack={() => {
                setSelectedClass(null);
                setViewMode(null);
              }}
            />
            <div className="actions-row">
              <QuizPanel
                classes={classes}
                selectedIds={selectedForQuiz}
                onToggle={(id, checked) =>
                  setSelectedForQuiz((prev) =>
                    checked ? [...prev, id] : prev.filter((x) => x !== id)
                  )
                }
                onGenerate={(ids) => {
                  // Integrate backend here
                  console.log("Generate quiz for:", ids);
                }}
              />
              <TeacherNotesPanel
                cls={selectedClass}
                value={notesByClass[selectedClass.id]}
                onChange={(val) =>
                  setNotesByClass((prev) => ({ ...prev, [selectedClass.id]: val }))
                }
                onClear={() =>
                  setNotesByClass((prev) => ({ ...prev, [selectedClass.id]: "" }))
                }
              />
            </div>
          </div>
        )}

        {/* Notes-only view when selecting via Add Notes */}
        {selectedClass && viewMode === "notes" && (
          <div className="right-column notes-only">
            <TeacherNotesPanel
              cls={selectedClass}
              value={notesByClass[selectedClass.id]}
              onChange={(val) =>
                setNotesByClass((prev) => ({ ...prev, [selectedClass.id]: val }))
              }
              onClear={() =>
                setNotesByClass((prev) => ({ ...prev, [selectedClass.id]: "" }))
              }
              onBack={() => {
                setSelectedClass(null);
                setViewMode(null);
              }}
              rows={10}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default Report;
