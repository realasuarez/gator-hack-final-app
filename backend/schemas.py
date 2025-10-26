from pydantic import BaseModel, ConfigDict # Import ConfigDict
from typing import Optional

class LectureResponse(BaseModel):
    id: int
    status: str
    transcript: Optional[str] = None
    summary: Optional[str] = None
    topics_json: Optional[str] = None
    quiz_json: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
    
class LectureUploadResponse(BaseModel):
    lecture_id: int
    status: str