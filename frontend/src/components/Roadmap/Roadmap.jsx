import React from "react";
import "./Roadmap.css";

const Roadmap = () => {
  const sampleData = {
    className: "CS101 - Class Name",
    lectures: [
      {
        title: "Lecture 1 -",
        modules: [
          {
            name: "Module 1:",
            topics: [
              { name: "Topic 1:", status: "hit" },
              { name: "Topic 2:", status: "pending" },
              { name: "Topic 3:", status: "miss" },
            ],
          },
          {
            name: "Module 2:",
            topics: [
              { name: "Topic 1:", status: "hit" },
              { name: "Topic 2:", status: "hit" },
            ],
          },
        ],
      },
    ],
  };

  return (
    <div className="roadmap">
      <h2>{sampleData.className}</h2>

      {sampleData.lectures.map((lecture, index) => (
        <div className="lecture-section" key={index}>
          <h3>{lecture.title}</h3>
          {lecture.modules.map((module, idx) => (
            <div key={idx}>
              <div className="module-name">{module.name}</div>
              <ul className="topic-list">
                {module.topics.map((topic, j) => (
                  <li
                    key={j}
                    className={
                      topic.status === "hit"
                        ? "topic-hit"
                        : topic.status === "miss"
                        ? "topic-miss"
                        : "topic-pending"
                    }
                  >
                    {topic.name}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default Roadmap;
