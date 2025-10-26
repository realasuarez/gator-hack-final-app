import React, { useEffect, useState } from "react";
import "./QuestionsPanel.css";

const QuestionsPanel = ({ selectedTopic }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (selectedTopic) {
      // Wait a tick to trigger the animation
      setTimeout(() => setIsVisible(true), 10);
    }
  }, [selectedTopic]);

  if (!selectedTopic) return null;

  const questions = [
    {
      id: 1,
      question: "What is polymorphism?",
      answer:
        "Polymorphism allows objects to take on many forms, typically through inheritance where subclasses override parent methods.",
    },
    {
      id: 2,
      question: "Explain recursion.",
      answer:
        "Recursion is when a function calls itself until a base condition is met, often used for problems like tree traversal or factorials.",
    },
    {
      id: 3,
      question: "When should inheritance be used?",
      answer:
        "Use inheritance when multiple classes share attributes or behavior that can be abstracted into a base class.",
    },
    {
      id: 4,
      question: "Difference between stack and heap memory?",
      answer:
        "Stack memory stores local variables and follows LIFO order, while heap memory stores dynamically allocated data.",
    },
  ];

  return (
    <div className={`questions-panel ${isVisible ? "active" : ""}`}>
      <div className="gradient-box">Questions per Topic</div>
      <div className="questions-list">
        {questions.map((q) => (
          <div key={q.id} className="question-item">
            <p className="question-text">
              <strong>Question {q.id}:</strong> {q.question}
            </p>
            <p className="answer-text">{q.answer}</p>
            <hr className="question-divider" />
          </div>
        ))}
      </div>
    </div>
  );
};

export default QuestionsPanel;
