import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ClassStats from "./pages/ClassStats";
import Report from "./pages/Report";

function App() {
  return (
    <Router>
      <Routes>
        {/* Homepage */}
        <Route path="/" element={<HomePage />} />

        {/* Class Analytics Page */}
        <Route path="/class-stats" element={<ClassStats />} />

        {/* Report Page (renamed from StudentStats) */}
        <Route path="/student-stats" element={<Report />} />
      </Routes>
    </Router>
  );
}

export default App;
