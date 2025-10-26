import React from "react";
import "./TopicsPanel.css";

const TopicsPanel = ({ topics, onSelectTopic }) => {
  return (
    <div className="topics-panel">
      <div className="gradient-box">Topics</div>
      <table>
        <thead>
          <tr>
            <th>Topic</th>
            <th>Questions</th>
          </tr>
        </thead>
        <tbody>
          {topics.map((t, index) => (
            <tr key={index} onClick={() => onSelectTopic && onSelectTopic(t)}>
              <td>{t.topic}</td>
              <td>{t.questions}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TopicsPanel;
