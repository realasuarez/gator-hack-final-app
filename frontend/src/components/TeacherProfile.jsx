// frontend/src/components/TeacherProfile.jsx
import React, { useEffect, useRef, useState } from "react";
import "./TeacherProfile.css";

const API_URL = import.meta.env.VITE_API_URL;

const TeacherProfile = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [activeOption, setActiveOption] = useState(null);
  const [inputValue, setInputValue] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");

  const toggleMenu = () => {
    if (activeOption) {
      setActiveOption(null);
    } else {
      setMenuOpen(!menuOpen);
    }
  };

  const handleOptionClick = (option) => {
    setActiveOption(option);
  };

  const handleBack = () => {
    setActiveOption(null);
    setInputValue("");
    setSelectedFile(null);
    setMessage("");
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setMessage("Please choose a file first.");
      return;
    }

    setUploading(true);
    setMessage("");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      // Choose the endpoint based on menu option
      const endpoint =
        activeOption === "Syllabus File"
          ? `${API_URL}/upload_syllabus/`
          : `${API_URL}/upload/`;

      const res = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
      const data = await res.json();

      setMessage(
        `✅ ${activeOption} uploaded successfully! ${
          data.lecture_id ? `Lecture ID: ${data.lecture_id}` : ""
        }`
      );
    } catch (err) {
      console.error(err);
      setMessage(`❌ Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const containerRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (!menuOpen) return;
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setMenuOpen(false);
        setActiveOption(null);
        setInputValue("");
        setSelectedFile(null);
        setMessage("");
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuOpen]);

  return (
    <div className="teacher-profile" ref={containerRef}>
      <div className="profile-card">
        <div className="profile-avatar"></div>
        <div className="profile-info">
          <h3>Dr. Teacher</h3>
          <p>University of Florida</p>
        </div>
        <button className="menu-button" onClick={toggleMenu}>
          ☰
        </button>
      </div>

      {menuOpen && (
        <div
          className={`dropdown-menu ${
            activeOption ? "expanded" : "collapsed"
          }`}
        >
          {!activeOption ? (
            <>
              {["Syllabus File", "Lecture File", "Audio File"].map((option) => (
                <button
                  key={option}
                  className="dropdown-option"
                  onClick={() => handleOptionClick(option)}
                >
                  {option}
                </button>
              ))}
            </>
          ) : (
            <div className="input-section">
              <button className="back-button" onClick={handleBack}>
                ← Back
              </button>
              <h4>{activeOption}</h4>

              {/* File upload input */}
              <input
                type="file"
                accept={
                  activeOption === "Syllabus File"
                    ? ".pdf,.doc,.docx"
                    : ".mp3,.wav,.m4a,.mp4"
                }
                onChange={(e) => setSelectedFile(e.target.files[0])}
              />

              <button
                className="submit-button"
                onClick={handleSubmit}
                disabled={uploading}
              >
                {uploading ? "Uploading..." : "Submit"}
              </button>

              {message && (
                <p
                  style={{
                    fontSize: "0.85rem",
                    color: message.startsWith("✅") ? "green" : "red",
                    marginTop: "0.5rem",
                  }}
                >
                  {message}
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TeacherProfile;
