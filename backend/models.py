from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="PROCESSING")
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    topics_json = Column(Text, nullable=True) # Will store the JSON as a string
    quiz_json = Column(Text, nullable=True)   # Will store the JSON as a string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    key_points_json = Column(Text, nullable=True) # For Key Points (Detailed Summary)
    examples_json = Column(Text, nullable=True)   # For Examples Used
    lda_topics_json = Column(Text, nullable=True) # For the gensim/nltk topics