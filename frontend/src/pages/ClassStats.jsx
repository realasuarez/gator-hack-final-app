import React, { useState } from "react";
import "./ClassStats.css";
import TopicsPanel from "../components/TopicsPanel";
import QuestionsPanel from "../components/QuestionsPanel";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Title, Tooltip, Legend);

const ClassStats = () => {
  const [selectedClass, setSelectedClass] = useState(null);
  const [selectedTopic, setSelectedTopic] = useState(null);

  const classData = [
    { name: "Class 1", questions: 5 },
    { name: "Class 2", questions: 3 },
    { name: "Class 3", questions: 7 },
    { name: "Class 4", questions: 4 },
    { name: "Class 5", questions: 6 },
  ];

  const topicData = [
    { topic: "Topic 1", questions: 3 },
    { topic: "Topic 2", questions: 5 },
    { topic: "Topic 3", questions: 2 },
    { topic: "Topic 4", questions: 4 },
  ];

  const chartData = {
    labels: classData.map((c) => c.name),
    datasets: [
      {
        label: "Questions",
        data: classData.map((c) => c.questions),
        borderColor: "#2563eb",
        backgroundColor: "rgba(37,99,235,0.2)",
        tension: 0.4,
      },
    ],
  };

  return (
    <div className="class-stats">
      <div className="header-row">
        <button className="back-button" onClick={() => (window.location.href = "/")}>Back</button>
        <h1 className="page-title">Class Analytics</h1>
      </div>

      <div className={`class-stats-container ${selectedTopic ? "three-columns" : ""}`}>
        {/* Left Panel - Class Concerns */}
        <div className="class-concerns">
          <div className="gradient-box">Class Concerns</div>
          <table>
            <thead>
              <tr>
                <th>Class</th>
                <th>Questions</th>
              </tr>
            </thead>
            <tbody>
              {classData.map((c, index) => (
                <tr
                  key={index}
                  onClick={() => {
                    setSelectedClass(c.name);
                    setSelectedTopic(null);
                  }}
                >
                  <td>{c.name}</td>
                  <td>{c.questions}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Right Panel - Graph (hidden when topic selected) */}
        {!selectedTopic && (
          <div className={`class-graph ${selectedClass ? "shrink" : ""}`}>
            <h2>Questions Per Class</h2>
            <Line data={chartData} />
          </div>
        )}

        {/* Topics Panel - Appears on click */}
        {selectedClass && (
          <TopicsPanel topics={topicData} onSelectTopic={(t) => setSelectedTopic(t)} />
        )}

        {/* Questions Panel - Appears on topic click */}
        {selectedTopic && <QuestionsPanel selectedTopic={selectedTopic} />}
      </div>
    </div>
  );
};

export default ClassStats;

