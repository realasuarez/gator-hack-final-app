import React, { useEffect, useState } from "react";
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

const API_URL = import.meta.env.VITE_API_URL;

const ClassStats = () => {
  const [classData, setClassData] = useState([]);
  const [selectedClass, setSelectedClass] = useState(null);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const res = await fetch(`${API_URL}/analytics/questions`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        setClassData(json.questions_per_class || []);
      } catch (err) {
        console.error("Error fetching class data:", err);
        setError("Failed to load class analytics.");
      }
    };
    fetchQuestions();
  }, []);

  const chartData = {
    labels: classData.map((c) => c.lecture_title || `Lecture ${c.id}`),
    datasets: [
      {
        label: "Questions per Class",
        data: classData.map((c) => c.total_questions || 0),
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

      {error && <p style={{ color: "red" }}>{error}</p>}

      <div className={`class-stats-container ${selectedTopic ? "three-columns" : ""}`}>
        {/* Left Panel */}
        <div className="class-concerns">
          <div className="gradient-box">Class Concerns</div>
          <table>
            <thead>
              <tr>
                <th>Lecture</th>
                <th>Questions</th>
              </tr>
            </thead>
            <tbody>
              {classData.map((c, index) => (
                <tr key={index} onClick={() => setSelectedClass(c.lecture_title)}>
                  <td>{c.lecture_title || `Lecture ${c.id}`}</td>
                  <td>{c.total_questions || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Graph */}
        <div className="class-graph">
          <h2>Questions Per Lecture</h2>
          <Line data={chartData} />
        </div>

        {/* Optional topic/question panels */}
        {selectedClass && (
          <TopicsPanel
            topics={classData.find((x) => x.lecture_title === selectedClass)?.topics || []}
            onSelectTopic={(t) => setSelectedTopic(t)}
          />
        )}
        {selectedTopic && <QuestionsPanel selectedTopic={selectedTopic} />}
      </div>
    </div>
  );
};

export default ClassStats;
