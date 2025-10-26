from sqlalchemy.orm import Session
from sqlalchemy import text
import json
import models
from fastapi import Depends
from database import get_db # Import the get_db dependency

class AnalyticsService:
    """
    A service class to handle all database analytics.
    It gets the db session injected by FastAPI.
    """
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    # ------------------------------
    # 1. Questions per Lecture
    # ------------------------------
    def get_questions_per_class(self):
        """
        Counts number of questions in quiz_json per lecture.
        """
        query = text("""
            SELECT id, json_array_length(quiz_json) AS question_count
            FROM lectures
            WHERE status = 'DONE'
            ORDER BY id;
        """)
        result = self.db.execute(query).fetchall()
        return [{"class_id": row[0], "questions": row[1]} for row in result]

    # ------------------------------
    # 2. Topics and Subtopics Count
    # ------------------------------
    def get_topics_overview(self):
        """
        Calculates number of topics and total subtopics per lecture.
        """
        lectures = self.db.query(models.Lecture).filter(models.Lecture.status == "DONE").all()
        output = []

        for lecture in lectures:
            try:
                topics = json.loads(lecture.topics_json or "[]")
                topic_count = len(topics)
                subtopics_count = sum(len(t.get("subtopics", [])) for t in topics)
            except Exception:
                topic_count = 0
                subtopics_count = 0

            output.append({
                "class_id": lecture.id,
                "topics": topic_count,
                "subtopics": subtopics_count
            })
        return output

    # ------------------------------
    # 3. Transcript Word Count
    # ------------------------------
    def get_transcript_length(self):
        """
        Computes number of words per transcript to track lecture depth.
        """
        query = text("""
            SELECT id, length(transcript) - length(replace(transcript, ' ', '')) + 1 AS word_count
            FROM lectures
            WHERE status = 'DONE';
        """)
        result = self.db.execute(query).fetchall()
        return [{"class_id": row[0], "word_count": row[1]} for row in result]

    # ------------------------------
    # 4. Summary Insights
    # ------------------------------
    def get_summary_metrics(self):
        """
        Extracts key metrics from summary JSON — main ideas and key takeaway presence.
        """
        lectures = self.db.query(models.Lecture).filter(models.Lecture.status == "DONE").all()
        output = []

        for lecture in lectures:
            try:
                summary_json = json.loads(lecture.summary or "{}")
                main_ideas = summary_json.get("mainIdeas", [])
                takeaway = summary_json.get("keyTakeaway", "")
            except Exception:
                main_ideas = []
                takeaway = ""

            output.append({
                "class_id": lecture.id,
                "main_ideas_count": len(main_ideas),
                "has_takeaway": bool(takeaway)
            })
        return output

    # ------------------------------
    # 5. Syllabus Coverage Estimate
    # ------------------------------
    def get_syllabus_coverage(self):
        """
        Approximates syllabus coverage as number of unique topics discussed so far.
        """
        lectures = self.db.query(models.Lecture).filter(models.Lecture.status == "DONE").all()
        all_topics = set()

        for lecture in lectures:
            try:
                topics = json.loads(lecture.topics_json or "[]")
                for t in topics:
                    all_topics.add(t.get("topic", ""))
            except Exception:
                pass

        total_unique_topics = len(all_topics)
        total_lectures = len(lectures)

        return {
            "unique_topics_covered": total_unique_topics,
            "lectures_count": total_lectures,
            "avg_topics_per_class": round(total_unique_topics / total_lectures, 2) if total_lectures > 0 else 0
        }

    # ------------------------------
    # 6. Lecture Timeline (for charting)
    # ------------------------------
    def get_lecture_timeline(self):
        """
        Returns lecture creation dates to help visualize class progression.
        """
        query = text("""
            SELECT id, date(created_at) AS date
            FROM lectures
            WHERE status = 'DONE'
            ORDER BY created_at;
        """)
        result = self.db.execute(query).fetchall()
        return [{"class_id": row[0], "date": row[1]} for row in result]

    # ------------------------------
    # 7. Combined Dashboard Metrics
    # ------------------------------
    def get_dashboard_metrics(self):
        """
        Combines all analytics into one dictionary.
        Ideal for the main dashboard endpoint.
        """
        return {
            "questions_per_class": self.get_questions_per_class(),
            "topics_overview": self.get_topics_overview(),
            "transcript_length": self.get_transcript_length(),
            "summary_metrics": self.get_summary_metrics(),
            "syllabus_coverage": self.get_syllabus_coverage(),
            "lecture_timeline": self.get_lecture_timeline()
        }
