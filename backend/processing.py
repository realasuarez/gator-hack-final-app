import shutil
import os
import json
import re
from sqlalchemy.orm import Session
import models
import database

# --- AI Imports ---
from openai import OpenAI
# from dotenv import load_dotenv # No longer needed here

# --- Imports for LDA ---
import nltk
import gensim
from nltk.corpus import stopwords
from gensim import corpora

# --- NLTK stopwords (will be handled in the class) ---
# stop_words = stopwords.words('english') # Moved to __init__


class ProcessingService:
    """
    A service class to handle all AI processing of lectures.
    It takes the OpenAI client as a dependency.
    """
    def __init__(self, client: OpenAI):
        self.client = client
        
        # --- Download NLTK stopwords (robustly) ---
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            print("Downloading NLTK stopwords...")
            nltk.download('stopwords')
        self.stop_words = stopwords.words('english')


    # --- Transcription Function ---
    def transcribe_with_whisper(self, file_path: str) -> str:
        print(f"Starting transcription for {file_path}...")
        with open(file_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create( # Use self.client
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
    def analyze_with_llm(self, transcribed_text: str) -> dict:
        print("Starting LLM analysis ...")
        
        prompt = f"""
          You are a **university-level lecture synthesis and academic content structuring assistant**.
          Your task is to carefully analyze the following **classroom transcript** and produce a **clear, comprehensive, and pedagogically organized summary** of the lecture.
          The goal is to transform raw spoken content into **instructionally valuable, publication-quality study notes**.

          Your output MUST be *only* a valid JSON object with **no extra commentary, markdown, or code fences.**
          The JSON object must include the following keys and subkeys **exactly as listed**:

          ---

          #### 1. "topicsCovered"
          A list of objects capturing the structure and flow of the lecture.
          Each object must include:
          - **"topic"** *(string)* — The primary subject or concept discussed.
          - **"subtopics"** *(list of strings)* — Subthemes or secondary concepts under that main topic, listed in the **order presented during the lecture**.
          - Include mention of any **transitions** between topics.

          ---

          #### 2. "keyPoints"
          A list of objects summarizing detailed explanations for each topic.
          Each object must include:
          - **"topic"** *(string)* — The topic these points relate to.
          - **"points"** *(list of strings)* — Multi-sentence, well-developed explanations of:
            - Definitions, reasoning, and conceptual elaboration;
            - Instructor arguments, examples, or key insights;
            - Comparisons, relationships, or cause–effect logic between ideas;
            - Any mentioned data, formulas, or specialized terminology (with contextual explanation);
            - Teaching cues or rhetorical clarifications that helped illustrate the concept.

          ---

          #### 3. "questionsAsked"
          A list of objects representing interactive dialogue and inquiry during the lecture.
          Each object must include:
          - **"question"** *(string)* — The exact or paraphrased question asked.
          - **"who asked"** *(string)* — "Identify who asked the question (Student, Instructor)." and specify who asked the question also specify "who_answered": "Identify who answered the question (Student, Instructor).
          - **"topic"** *(string)* — The specific topic or subtopic the question relates to.
          - **"answer"** *(string)* — A complete explanation of the response given.
          - **"learningValue"** *(string)* — A short description of how this question-and-answer exchange deepened understanding.

          ---

          #### 4. "examplesUsed"
          A list of objects documenting all illustrative materials used in the lecture.
          Each object must include:
          - **"example"** *(string)* — The name or short description of the example, case study, or analogy.
          - **"topic"** *(string)* — The concept or theory it was meant to illustrate.
          - **"explanation"** *(string)* — A step-by-step explanation of how the example clarified, simplified, or contextualized the concept.
          - **"connectionToConcept"** *(string)* — How this example reinforced theoretical understanding or bridged abstract ideas to practical applications.

          ---

          #### 5. "summaryInsight"
          An object synthesizing the full lecture meaning and pedagogical message.
          This object must include:
          - **"mainIdeas"** *(list of strings)* — A cohesive synthesis of the lecture’s major themes, structured in logical flow.
          - **"keyTakeaway"** *(string)* — The central conceptual or applied insight that the instructor wanted students to retain.
          - **"connectionToBroaderCourseThemes"** *(string)* — A reflection on how this lecture ties into broader course objectives, future lessons, or real-world implications.

          ---

          Transcript:
          {transcribed_text}
          """

        response = self.client.chat.completions.create( # Use self.client
            model="llama-3.3-70b-instruct",
            messages=[
                {"role": "system", "content": "You are an academic teaching analyst who processes classroom transcripts into structured insights for teachers. Your output must be a valid JSON object."},
                {"role": "user", "content": prompt}
            ],
            extra_body={
                "metadata": {"generation_name": "class_topic_analytics_split", "trace_user_id": "faculty_demo"}
            }
        )

        # Clean and parse the JSON response
        try:
            data = json.loads(response.choices[0].message.content)
            print("LLM analysis (enhanced) complete and parsed.")
            return data
        except json.JSONDecodeError:
            print("Attempting to clean and parse JSON...")
            cleaned = re.sub(r"```json\n|```", "", response.choices[0].message.content)
            try:
                data = json.loads(cleaned)
                print("LLM analysis complete and parsed after cleaning.")
                return data
            except Exception as e:
                print(f"Failed to parse JSON even after cleaning: {e}")
                return {"error": "Failed to parse LLM response"}
            
    # --- FUNCTION FOR CLASS NOTES ---
    def generate_pedagogical_notes(self, transcribed_text: str) -> dict:
        """
        Generates rich, structured pedagogical notes.
        """
        print("Starting rich pedagogical notes generation (from IPYNB Cell 10)...")
        
        # This is the prompt from Cell 10 of the notebook
        prompt = f"""
          You are a **university-level instructional designer and academic content synthesis expert**,
          tasked with producing **final, publication-quality lecture notes** from a full classroom transcript.

          Your notes must read like a **complete, pedagogically designed lecture document**, suitable for:
          - student distribution, and
          - instructor delivery as a teaching script.

          ---

          ### PRIMARY OBJECTIVE
          Transform the transcript into **cohesive, detailed, and instructionally sound notes** that:
          - present **full conceptual explanations** with reasoning and examples,
          - integrate **instructor cues, real-world analogies, and examples** fluidly,
          - maintain a **didactic structure** (Introduction → Subtopics → Explanations → Applications → Summary),
          - and sound **formally academic yet conversational**, as if read aloud in a university lecture.

          Avoid shallow or one-line answers. Every list item or point must be **multi-sentence, explanatory, and instructional**.

          ---

          ### OUTPUT FORMAT
          Return a **single valid JSON object** with this structure:

          {{
            "main_topic": "...",
            "learning_objectives": ["..."],
            "introduction": "Provide a complete paragraph introducing the topic, its context, relevance, and how it connects to prior or future lectures.",
            "subtopics": ["..."],
            "key_points": [
              {{
                "subtopic": "...",
                "points": [
                  "Each point should be a multi-sentence paragraph explaining the idea, including what it is, why it matters, and how it fits within the lecture theme."
                ]
              }}
            ],
            "examples_and_explanations": [
              {{
                "subtopic": "...",
                "example": "Clearly name or describe the example used by the instructor.",
                "step_by_step_explanation": "Explain the example step by step, connecting each part to underlying principles or theories.",
                "connection_to_concept": "Discuss what this example teaches or clarifies about the concept."
              }}
            ],
            "case_studies_or_applications": [
              {{
                "context": "Specify the practical or real-world setting.",
                "description": "Summarize what occurred or was discussed.",
                "lesson": "Explain what conceptual or applied insight the case illustrates."
              }}
            ],
            "comparisons": [
              {{
                "concept": "State the two items or paradigms compared.",
                "feature_a": "Describe feature or approach A in detail.",
                "feature_b": "Describe feature or approach B in detail.",
                "difference": "Offer a clear, paragraph-length discussion of how and why they differ and when each is preferred."
              }}
            ],
            "activities_or_demonstrations": [
              {{
                "activity": "Describe the classroom or lab activity.",
                "purpose": "Explain the learning goal behind the activity.",
                "process": "Provide sequential steps or what students were asked to do.",
                "key_takeaway": "Summarize the conceptual or skill-based understanding gained."
              }}
            ],
            "terminology_and_definitions": [
              {{
                "term": "List one technical term or keyword.",
                "definition": "Provide a full-sentence, contextual definition that captures meaning and relevance.",
                "context_used": "Indicate where or how it appeared during the lecture."
              }}
            ],
            "instructor_tips_and_analogies": [
              {{
                "analogy_or_tip": "Include any analogy, metaphor, or teaching shortcut mentioned.",
                "purpose": "Explain what aspect of understanding this analogy clarifies or simplifies.",
                "teaching_note": "Add how the instructor framed, demonstrated, or emphasized this analogy in class."
              }}
            ],
            "questions_and_answers": [
              {{
                "question": "Write the student’s or instructor’s question in full.",
                "answer": "Write the complete answer or explanation given.",
                "who_asked": "Identify who asked the question (Student, Instructor).",
                "who_answered": "Identify who answered the question (Student, Instructor).",
                "teaching_value": "Explain"
              }}
            ],
            "summary_and_conclusion": "Compose a multi-paragraph synthesis that ties all subtopics together, reiterates significance, and reinforces overarching principles. Integrate reflection on applications or implications if relevant.",
            "key_takeaways": [
              "Write 3–5 complete, memorable sentences capturing the main conceptual lessons of the lecture."
            ],
            "highlighted_insight": "**Write one powerful, bolded statement summarizing the lecture’s central insight or message.**"
          }}

          ---
          Transcript:
          {transcribed_text}
          """

        response = self.client.chat.completions.create( # Use self.client
            model="llama-3.3-70b-instruct",
            messages=[
                {"role": "system", "content": "You must output a single valid JSON object only. No markdown, commentary, or preamble."},
                {"role": "user", "content": prompt}
            ],
            extra_body={
                "metadata": {"generation_name": "pedagogical_notes_generation", "trace_user_id": "faculty_demo"}
            }
        )

        # Use the robust parsing logic
        try:
            data = json.loads(response.choices[0].message.content)
            print("Pedagogical notes generated and parsed.")
            return data
        except json.JSONDecodeError:
            print("Attempting to clean and parse notes JSON...")
            cleaned = re.sub(r"```json\n|```", "", response.choices[0].message.content.strip(), flags=re.MULTILINE)
            try:
                data = json.loads(cleaned)
                print("Pedagogical notes complete and parsed after cleaning.")
                return data
            except Exception as e:
                print(f"Failed to parse notes JSON even after cleaning: {e}")
                return {"error": "Failed to parse LLM response for notes"}

    # --- LDA Topic Function ---
    def get_lda_topics(self, transcribed_text: str) -> list:
        print("Starting LDA topic analysis...")
        try:
            # Use self.stop_words
            tokens = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', transcribed_text) if w.lower() not in self.stop_words]
            
            if not tokens:
                print("No valid tokens found for LDA after filtering.")
                return ["No topics generated (short transcript)."]

            dictionary = corpora.Dictionary([tokens])
            corpus = [dictionary.doc2bow(tokens)]
            lda_model = gensim.models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=3, passes=10)

            topics_list = []
            for idx, topic in lda_model.print_topics(num_words=5):
                topics_list.append(f"Topic {idx+1}: {topic}")
            
            print("LDA analysis complete.")
            return topics_list
        except Exception as e:
            print(f"LDA analysis failed: {e}")
            return []


    # --- Background Job Function ---
    def process_lecture_file(self, lecture_id: int, file_path: str):
        print(f"Starting REAL processing for lecture {lecture_id} at {file_path}")
        
        # This is the correct pattern for a background task
        db = database.SessionLocal()
        
        try:
            # 1. Get the lecture entry
            lecture = db.query(models.Lecture).filter(models.Lecture.id == lecture_id).first()
            if not lecture:
                print(f"Error: Lecture {lecture_id} not found.")
                return

            # 2. Run REAL Transcription (calling its own method)
            transcript_text = self.transcribe_with_whisper(file_path)
            
            lecture.transcript = transcript_text
            db.commit()
            print(f"Lecture {lecture_id}: Transcript saved.")

            # 3. Run REAL Analysis (calling its own method)
            analysis_data = self.analyze_with_llm(transcript_text)
            
            if "error" in analysis_data:
                raise Exception(analysis_data["error"])

            # 4. Run LDA Topic Modeling (calling its own method)
            lda_topics_list = self.get_lda_topics(transcript_text)

            # 5. Map ALL results back to your original DB columns
            lecture.summary = json.dumps(analysis_data.get("summaryInsight", {}))
            lecture.topics_json = json.dumps(analysis_data.get("topicsCovered", []))
            lecture.quiz_json = json.dumps(analysis_data.get("questionsAsked", []))
            lecture.key_points_json = json.dumps(analysis_data.get("keyPoints", []))
            lecture.examples_json = json.dumps(analysis_data.get("examplesUsed", []))
            lecture.lda_topics_json = json.dumps(lda_topics_list)
            
            # 6. Mark as DONE
            lecture.status = "DONE"
            db.commit()
            print(f"Successfully processed lecture {lecture_id}")

        except Exception as e:
            print(f"Failed to process lecture {lecture_id}. Error: {e}")
            db.rollback()
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
