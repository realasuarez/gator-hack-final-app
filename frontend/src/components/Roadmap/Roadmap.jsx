import React from "react";
import "./Roadmap.css";

const Roadmap = ({ roadmapData }) => {
  if (!roadmapData) {
    return <p className="no-data">No class information yet...</p>;
  }

  const topics = roadmapData.topics || [];
  const subtopics = roadmapData.subtopics || {};

  return (
    <div className="roadmap">
      <h2>📘 Extracted Syllabus Topics</h2>
      {topics.map((topic, index) => (
        <div className="lecture-section" key={index}>
          <h3>{topic}</h3>
          <ul className="topic-list">
            {(subtopics[topic] || []).map((sub, i) => (
              <li key={i} className="topic-pending">
                {sub}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default Roadmap;
