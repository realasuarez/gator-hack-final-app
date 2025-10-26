import React from "react";
import "./LectureSection.css";

const LectureSection = ({ lecture }) => {
  console.log("Rendering LectureSection:", lecture); // check console

  if (!lecture) {
    return <div style={{ color: "red" }}>No lecture data</div>;
  }

  return (
    <div className="lecture-section">
      <h3>{lecture.title}</h3>
      {Array.isArray(lecture.modules) ? (
        lecture.modules.map((module, idx) => (
          <div className="module" key={idx}>
            <strong className="module-name">{module.name}</strong>
            <ul className="topic-list">
              {Array.isArray(module.topics) ? (
                module.topics.map((t, j) => <li key={j}>{t}</li>)
              ) : (
                <li>No topics</li>
              )}
            </ul>
          </div>
        ))
      ) : (
        <p>No modules</p>
      )}
    </div>
  );
};

export default LectureSection;
