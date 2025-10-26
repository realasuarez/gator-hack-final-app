import React from "react";

// Reusable, data-ready summary shell for a class
// Props: cls { id, code, name, term, students }
const ClassSummary = ({ cls }) => {
  if (!cls) return null;
  return (
    <div>
      <div className="gradient-box">Class Summary</div>
      <h2>
        {cls.code} — {cls.name}
      </h2>
      <p>Term: {cls.term}</p>
      <p>Enrolled Students: {cls.students}</p>
      <div style={{ opacity: 0.7, marginTop: "0.5rem" }}>
        Backend-ready placeholder. Inject metrics, charts, and insights here.
      </div>
    </div>
  );
};

export default ClassSummary;

