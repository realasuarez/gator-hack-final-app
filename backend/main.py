import shutil
import os
from fastapi import BackgroundTasks, HTTPException, Depends, UploadFile, File, FastAPI
from sqlalchemy.orm import Session
from typing import List

import database
import models
import schemas
import processing
import analytics
# import syllabus_tracker

# --------------------------------------------
# Database Dependency
# --------------------------------------------
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ensure upload directory exists
os.makedirs("temp_uploads", exist_ok=True)

# Initialize FastAPI app
app = FastAPI(title="Professor Lecture Analytics API")

print("--- 1. RUNNING main.py ---")
print(f"--- 2. Current Directory: {os.getcwd()} ---")

# Create the database tables
try:
    models.Base.metadata.create_all(bind=database.engine)
    print("--- 3. Database tables created successfully (or already exist) ---")
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

    # 3. Process in background
    background_tasks.add_task(
        processing.process_lecture_file,
        lecture_id=new_lecture.id,
        file_path=file_path
    )

    # 4. Return immediate response
    return {"lecture_id": new_lecture.id, "status": "PROCESSING"}

# --------------------------------------------
# ANALYTICS ROUTES
# --------------------------------------------

@app.get("/analytics/questions")
def get_questions_per_class(db: Session = Depends(get_db)):
    """
    Returns total number of questions for each lecture.
    """
    data = analytics.get_questions_per_class(db)
    return {"questions_per_class": data}


@app.get("/analytics/topics")
def get_topics_overview(db: Session = Depends(get_db)):
    """
    Returns topic and subtopic counts per lecture.
    """
    data = analytics.get_topics_overview(db)
    return {"topics_overview": data}


@app.get("/analytics/summary")
def get_summary_metrics(db: Session = Depends(get_db)):
    """
    Returns summary insights like number of main ideas and key takeaway presence.
    """
    data = analytics.get_summary_metrics(db)
    return {"summary_metrics": data}


@app.get("/analytics/syllabus")
def get_syllabus_coverage(db: Session = Depends(get_db)):
    """
    Returns syllabus coverage metrics.
    """
    data = analytics.get_syllabus_coverage(db)
    return {"syllabus_coverage": data}


@app.get("/analytics/dashboard")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Returns all key metrics combined — ideal for main dashboard.
    """
    data = analytics.get_dashboard_metrics(db)
    return data

# -------------------------
# SYLLABUS TRACKING ENDPOINTS
# -------------------------

# @app.post("/upload_syllabus/")
# async def upload_syllabus(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db)
# ):
#     """
#     Upload a syllabus (PDF or DOCX) and compute coverage stats
#     by comparing it against lecture topics.
#     """
#     upload_dir = "temp_uploads/syllabus"
#     os.makedirs(upload_dir, exist_ok=True)
#     file_path = os.path.join(upload_dir, file.filename)

#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     try:
#         result = syllabus_tracker.process_syllabus_file(file_path, db)
#         syllabus_tracker.save_coverage_result(result, file.filename)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Syllabus processing failed: {e}")

#     return {"filename": file.filename, "coverage_result": result}

# @app.get("/syllabus_result/")
# def get_latest_syllabus_result():
#     """
#     Returns the most recently saved syllabus coverage JSON.
#     """
#     latest = syllabus_tracker.get_latest_coverage_result()
#     if not latest:
#         raise HTTPException(status_code=404, detail="No syllabus result found yet.")
#     return latest

# --------------------------------------------