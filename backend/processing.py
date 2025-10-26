import shutil
import os
import json
import re
from sqlalchemy.orm import Session
import models
import database

# --- AI Imports ---
from openai import OpenAI
from dotenv import load_dotenv

# --- Imports for LDA ---
import nltk
import gensim
from nltk.corpus import stopwords
from gensim import corpora

# --- Load .env file ---
load_dotenv()

# --- Initialize OpenAI Client ---
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE"),
)

# --- Download NLTK stopwords (robustly) ---
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading NLTK stopwords...")
    nltk.download('stopwords')
stop_words = stopwords.words('english')


# --- Transcription Function ---
def transcribe_with_whisper(file_path: str) -> str:
    print(f"Starting transcription for {file_path}...")
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_file,
            extra_body={
                "metadata": {
                    "generation_name": "lecture_transcription",
                    "trace_user_id": "faculty_hackathon_demo"
                }
            }
        )
    print("Transcription complete.")
    return transcript.text

# --- Analysis Function ---

def analyze_with_llm(transcribed_text: str) -> dict:
    print("Starting LLM analysis...")
    
    prompt = f"""
    You are an academic teaching analyst. Analyze the following lecture transcript and return a structured JSON object.
    Your output MUST be *only* the JSON object, with no other text.
    
    The JSON object must use the following exact keys:
    - "topicsCovered": A list of objects, where each object has a "topic" (string) and "subtopics" (list of strings).
    - "keyPoints": A list of objects, where each object has a "topic" (string) and "points" (list of strings).
    - "questionsAsked": A list of objects, where each object has a "question" (string), "type" (string), and "answer" (string).
    - "examplesUsed": A list of objects, where each object has an "example" (string), "topic" (string), and "explanation" (string).
    - "summaryInsight": An object with "mainIdeas" (list of strings), "keyTakeaway" (string), and "connectionToBroaderCourseThemes" (string).

    Use the detailed instructions below to populate each key:
    
    1. For "topicsCovered":
    Identify all main topics and subtopics in the exact order they appeared.
    Highlight transitions between themes.
    
    2. For "keyPoints":
    Provide thorough, bullet-point explanations under each topic and subtopic.
    Include definitions, explanations, arguments, and important details.
    
    3. For "questionsAsked":
    List all questions posed.
    Indicate if they were rhetorical, discussion-based, or comprehension checks.
    
    4. For "examplesUsed":
    Record any examples, case studies, or analogies mentioned.
    Briefly explain how each example illustrated a concept.
    
    5. For "summaryInsight":
    Conclude with a concise synthesis of the lecture’s main ideas and the overall learning objective.

    Transcript:
    {transcribed_text}
    """

    response = client.chat.completions.create(
        model="llama-3.1-70b-instruct",
        messages=[
            {"role": "system", "content": "You are an academic teaching analyst who processes classroom transcripts into structured insights for teachers. Your output must be a valid JSON object."},
            {"role": "user", "content": prompt}
        ],
        extra_body={
            "metadata": {"generation_name": "class_topic_analytics", "trace_user_id": "faculty_demo"}
        }
    )

    # Clean and parse the JSON response
    try:
        data = json.loads(response.choices[0].message.content)
        print("LLM analysis complete and parsed.")
        
        # --- print statement for debugging ---
        # print(json.dumps(data, indent=2)) 
        
        return data
    except json.JSONDecodeError:
        print("Attempting to clean and parse JSON...")
        cleaned = re.sub(r"```json\n|```", "", response.choices[0].message.content)
        try:
            data = json.loads(cleaned)
            print("LLM analysis complete and parsed after cleaning.")
            
            # --- print statement for debugging ---
            # print(json.dumps(data, indent=2)) 
            
            return data
        except Exception as e:
            print(f"Failed to parse JSON even after cleaning: {e}")
            return {"error": "Failed to parse LLM response"}

# --- LDA Topic Function ---
def get_lda_topics(transcribed_text: str) -> list:
    print("Starting LDA topic analysis...")
    try:
        # Preprocess transcript into tokens
        tokens = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', transcribed_text) if w.lower() not in stop_words]
        
        # --- Add a check to prevent crash if tokens are still empty ---
        if not tokens:
            print("No valid tokens found for LDA after filtering.")
            return ["No topics generated (short transcript)."]

        dictionary = corpora.Dictionary([tokens])
        corpus = [dictionary.doc2bow(tokens)]

        # LDA Topic Model (Simple 3-topic split)
        lda_model = gensim.models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=3, passes=10)

        topics_list = []
        for idx, topic in lda_model.print_topics(num_words=5):
            topics_list.append(f"Topic {idx+1}: {topic}")
        
        print("LDA analysis complete.")
        return topics_list
    except Exception as e:
        print(f"LDA analysis failed: {e}")
        return [] # Return empty list on failure


# --- Background Job Function ---
def process_lecture_file(lecture_id: int, file_path: str):
    print(f"Starting REAL processing for lecture {lecture_id} at {file_path}")
    
    db = database.SessionLocal()
    
    try:
        # 1. Get the lecture entry
        lecture = db.query(models.Lecture).filter(models.Lecture.id == lecture_id).first()
        if not lecture:
            print(f"Error: Lecture {lecture_id} not found.")
            return

        # 2. Run REAL Transcription
        transcript_text = transcribe_with_whisper(file_path)
        
        lecture.transcript = transcript_text
        db.commit()
        print(f"Lecture {lecture_id}: Transcript saved.")

        # 3. Run REAL Analysis (One call for all data)
        analysis_data = analyze_with_llm(transcript_text)
        
        if "error" in analysis_data:
            raise Exception(analysis_data["error"])

        # 4. Run LDA Topic Modeling
        lda_topics_list = get_lda_topics(transcript_text)

        # 5. Map ALL results to our existing DB columns
        # We use json.dumps to store the Python list/dict as a JSON string
        
        # --- EXISTING ---
        lecture.summary = json.dumps(analysis_data.get("summaryInsight", {}))
        lecture.topics_json = json.dumps(analysis_data.get("topicsCovered", []))
        lecture.quiz_json = json.dumps(analysis_data.get("questionsAsked", []))
        
        # --- NEWLY ADDED ---
        lecture.key_points_json = json.dumps(analysis_data.get("keyPoints", []))
        lecture.examples_json = json.dumps(analysis_data.get("examplesUsed", []))
        lecture.lda_topics_json = json.dumps(lda_topics_list) # Save the new LDA topics
        
        # 6. Mark as DONE
        lecture.status = "DONE"
        db.commit()
        print(f"Successfully processed lecture {lecture_id}")

    except Exception as e:
        print(f"Failed to process lecture {lecture_id}. Error: {e}")
        # Rollback any partial commits on error
        db.rollback()
        # Try to get the lecture object again to update status
        lecture = db.query(models.Lecture).filter(models.Lecture.id == lecture_id).first()
        if lecture:
            lecture.status = "FAILED"
            db.commit()
    finally:
        # 7. Clean up the temp file
        upload_dir = os.path.dirname(file_path)
        if os.path.exists(upload_dir):
            shutil.rmtree(upload_dir)
            print(f"Cleaned up temp files in {upload_dir}")
        db.close()