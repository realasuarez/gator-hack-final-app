import shutil
import os
from fastapi import BackgroundTasks, HTTPException, Depends, UploadFile, File, FastAPI
from sqlalchemy.orm import Session
from typing import List
import json
import database
import models
import schemas

# --- NEW SERVICE IMPORTS ---
from processing import ProcessingService
from analytics import AnalyticsService
from syllabus_tracker import SyllabusService
from database import get_db, engine # Import get_db from database

# --- NEW: AI and .env IMPORTS ---
from openai import OpenAI
from dotenv import load_dotenv

# --------------------------------------------
# Application-level Setup
# --------------------------------------------
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
print("--- 1. RUNNING main.py ---")
print(f"--- 2. Current Directory: {os.getcwd()} ---")

# Ensure upload directory exists
os.makedirs("temp_uploads", exist_ok=True)

# Create a single, app-lifetime OpenAI client
try:
    llm_client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_API_BASE"),
    )
    print("--- 3. OpenAI client initialized ---")
except Exception as e:
    print(f"--- X. ERROR initializing OpenAI client: {e} ---")
    llm_client = None # Handle potential failure

# Create app-lifetime service instances
# These services live for the duration of the app
processing_service = ProcessingService(client=llm_client)
syllabus_service = SyllabusService(
    client=llm_client,
    results_dir="temp_uploads/syllabus_results"
)
print("--- 4. Services initialized ---")

# Initialize FastAPI app
app = FastAPI(title="Professor Lecture Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the database tables
try:
    models.Base.metadata.create_all(bind=database.engine)
    print("--- 5. Database tables created successfully (or already exist) ---")
except Exception as e:
    print(f"--- X. ERROR creating database: {e} ---")

# --------------------------------------------
# BASIC ROUTES
# --------------------------------------------
@app.get("/")
def read_root():
    return {"message": "Hello Professors! This API provides class analytics."}

@app.get("/lecture/{lecture_id}", response_model=schemas.LectureResponse)
def get_lecture_status(lecture_id: int, db: Session = Depends(get_db)):
    lecture = db.query(models.Lecture).filter(models.Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return lecture

@app.post("/upload/", response_model=schemas.LectureUploadResponse)
async def upload_lecture(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Create DB entry
    new_lecture = models.Lecture(status="PROCESSING")
    db.add(new_lecture)
    db.commit()
    db.refresh(new_lecture)

    # 2. Save uploaded file
    upload_dir = f"temp_uploads/lecture_{new_lecture.id}"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Process in background (USING THE SERVICE)
    background_tasks.add_task(
        processing_service.process_lecture_file, # Use the service method
        lecture_id=new_lecture.id,
        file_path=file_path
    )

    # 4. Return immediate response
    return {"lecture_id": new_lecture.id, "status": "PROCESSING"}

@app.get("/lecture/{lecture_id}/notes")
def get_lecture_notes(lecture_id: int, db: Session = Depends(get_db)):
    """
    Returns the full, pedagogically structured class notes as a JSON object
    (from the new 'notes_json' column).
    """
    lecture = db.query(models.Lecture).filter(models.Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    if lecture.status == "PROCESSING":
        raise HTTPException(status_code=400, detail="Lecture is still processing. Notes are not yet available.")
    
    if not lecture.notes_json:
        raise HTTPException(status_code=404, detail="Notes were not found or could not be generated for this lecture.")
    
    # Parse the string from the DB into a real JSON object
    try:
        notes_object = json.loads(lecture.notes_json)
        return notes_object
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse the stored notes JSON.")

# --------------------------------------------
# ANALYTICS ROUTES (Refactored to use AnalyticsService)
# --------------------------------------------

@app.get("/analytics/questions")
def get_questions_per_class(service: AnalyticsService = Depends(AnalyticsService)):
    """
    Returns total number of questions for each lecture.
    """
    data = service.get_questions_per_class()
    return {"questions_per_class": data}


@app.get("/analytics/topics")
def get_topics_overview(service: AnalyticsService = Depends(AnalyticsService)):
    """
    Returns topic and subtopic counts per lecture.
    """
    data = service.get_topics_overview()
    return {"topics_overview": data}


@app.get("/analytics/summary")
def get_summary_metrics(service: AnalyticsService = Depends(AnalyticsService)):
    """
    Returns summary insights like number of main ideas and key takeaway presence.
    """
    data = service.get_summary_metrics()
    return {"summary_metrics": data}


@app.get("/analytics/syllabus")
def get_syllabus_coverage(service: AnalyticsService = Depends(AnalyticsService)):
    """
    Returns syllabus coverage metrics.
    """
    data = service.get_syllabus_coverage()
    return {"syllabus_coverage": data}


@app.get("/analytics/dashboard")
def get_dashboard_metrics(service: AnalyticsService = Depends(AnalyticsService)):
    """
    Returns all key metrics combined — ideal for main dashboard.
    """
    data = service.get_dashboard_metrics()
    return data

# -------------------------
# SYLLABUS TRACKING ENDPOINTS (Refactored to use SyllabusService)
# -------------------------

@app.post("/upload_syllabus/")
async def upload_syllabus(
    file: UploadFile = File(...),
    db: Session = Depends(get_db) # Get the request-scoped db session
):
    """
    Upload a syllabus (PDF or DOCX) and compute coverage stats
    by comparing it against lecture topics.
    """
    upload_dir = "temp_uploads/syllabus"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Use the service instance and pass the db session
        result = syllabus_service.process_syllabus_file(file_path, db)
        # Note: saving the result is now handled *inside* the service method
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Syllabus processing failed: {str(e)}")

    return {"filename": file.filename, "coverage_result": result}

@app.get("/syllabus_result/")
def get_latest_syllabus_result():
    """
    Returns the most recently saved syllabus coverage JSON.
    """
    # Use the service instance
    latest = syllabus_service.get_latest_coverage_result()
    if not latest:
        raise HTTPException(status_code=404, detail="No syllabus result found yet.")
    return latest

@app.get("/syllabus/topics")
def get_syllabus_topics():
    """
    Returns a structured JSON list of main_topics and subtopics
    from the latest processed syllabus.
    """
    topic_list = syllabus_service.get_syllabus_topic_structure()
    
    if topic_list is None:
        raise HTTPException(status_code=404, detail="No syllabus result found yet. Please upload one first.")
    
    return topic_list

# --------------------------------------------
# END OF FILE
# --------------------------------------------
