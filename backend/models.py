from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="PROCESSING")
    transcript = Column(Text, nullable=True)
    
    summary = Column(Text, nullable=True)         # For "summaryInsight"
    topics_json = Column(Text, nullable=True)   # For "topicsCovered"
    quiz_json = Column(Text, nullable=True)     # For "questionsAsked"
    key_points_json = Column(Text, nullable=True) # For "keyPoints"
    examples_json = Column(Text, nullable=True)   # For "examplesUsed"
    lda_topics_json = Column(Text, nullable=True) # For the gensim/nltk topics
    notes_json = Column(Text, nullable=True)      # For the rich notes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
