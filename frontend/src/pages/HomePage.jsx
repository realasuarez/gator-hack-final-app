import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Roadmap from "../components/Roadmap/Roadmap";
import TeacherProfile from "../components/TeacherProfile";
import "./HomePage.css";

const HomePage = () => {
  const navigate = useNavigate();

  // 🌟 New state to hold the AI-generated roadmap
  const [roadmapData, setRoadmapData] = useState(null);

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <h1 className="dashboard-title">Dashboard</h1>

        {/* Pass the update function to TeacherProfile */}
        <TeacherProfile onRoadmapUpdate={setRoadmapData} />
      </header>

      {/* Main Section */}
      <div className="dashboard-main">
        {/* Sidebar - Roadmap */}
        <aside className="dashboard-sidebar">
          <h2 className="gradient-box">Semester Lectures</h2>

          {/* Pass roadmap data to Roadmap */}
          <Roadmap roadmapData={roadmapData} />
        </aside>

        {/* Main dashboard area */}
        <section className="dashboard-body">
          <div className="stats-row">
            <div
              className="stats-card student"
              onClick={() => navigate("/student-stats")}
            >
              <div className="stats-icon">🎓</div>
              <div className="stats-info">
                <h3>Reports</h3>
                <p>View report</p>
              </div>
            </div>

            <div
              className="stats-card class"
              onClick={() => navigate("/class-stats")}
            >
              <div className="stats-icon">🏫</div>
              <div className="stats-info">
                <h3>Class Analytics</h3>
                <p>View class statistics</p>
              </div>
            </div>
          </div>

          <div className="welcome-section">
            <h2>Course Analytics:</h2>
            <p>
              Use the semester roadmap to track syllabus coverage and lecture progress.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
};

export default HomePage;
