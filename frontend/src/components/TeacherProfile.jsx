import React, { useEffect, useRef, useState } from "react";
import "./TeacherProfile.css";

const TeacherProfile = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [activeOption, setActiveOption] = useState(null);
  const [inputValue, setInputValue] = useState("");

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
  };

  const containerRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (!menuOpen) return;
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setMenuOpen(false);
        setActiveOption(null);
        setInputValue("");
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
              {["Class Input", "Lecture", "Audio File"].map((option) => (
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
              <input
                type="text"
                placeholder={`Enter your ${activeOption.toLowerCase()}`}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
              />
              <button className="submit-button">Submit</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TeacherProfile;
