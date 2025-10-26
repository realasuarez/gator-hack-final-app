import React, { useEffect, useState } from "react";
import "./QuestionsPanel.css";

const QuestionsPanel = ({ selectedTopic }) => {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const API_URL = import.meta.env.VITE_API_URL;

  useEffect(() => {
    if (!selectedTopic) return;

    const fetchQuestions = async () => {
      try {
        setLoading(true);
        const res = await fetch(`${API_URL}/analytics/questions`);
        const data = await res.json();

        // You can modify this depending on how your backend structures topic-level questions
        const topicQuestions = data.questions_per_class?.filter(
          (q) => q.topic === selectedTopic
        );
        setQuestions(topicQuestions || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchQuestions();
  }, [selectedTopic, API_URL]);

  if (!selectedTopic) return null;
  if (loading) return <p style={{ textAlign: "center" }}>Loading questions...</p>;

  return (
    <div className="questions-panel active">
      <div className="gradient-box">Questions per Topic</div>
      <div className="questions-list">
        {questions.length === 0 ? (
          <p>No questions available for this topic yet.</p>
        ) : (
          questions.map((q, i) => (
            <div key={i} className="question-item">
              <p className="question-text">
                <strong>Question:</strong> {q.question}
              </p>
              <p className="answer-text">{q.answer}</p>
              <hr className="question-divider" />
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default QuestionsPanel;
