from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import speech_recognition as sr
from errors import AppError, handle_app_error, handle_unexpected_error
from agent.transcribe import transcribe_conversation
from agent.llm_supervisor import evaluate_call_with_llm
from errors import AppError

app = Flask(__name__)
CORS(app)

app.register_error_handler(AppError, handle_app_error)
app.register_error_handler(Exception, handle_unexpected_error)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

def transcribe_conversation(folder_path: str) -> str:
    recognizer = sr.Recognizer()
    files = sorted(os.listdir(folder_path), key=lambda x: (x.split()[0], x))
    full_text = ""

    for f in files:
        if not f.lower().endswith(".wav"):
            continue

        file_path = os.path.join(folder_path, f)

        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE_BYTES:
            full_text += f"{f}: [خطا: حجم فایل بیشتر از {MAX_FILE_SIZE_MB} مگابایت است]\n"
            continue

        try:
            with sr.AudioFile(file_path) as source:
                audio_data = recognizer.record(source)

            text = recognizer.recognize_google(
                audio_data,
                language="fa-IR"
            )

        except sr.UnknownValueError:
            text = "[نامفهوم]"
        except sr.RequestError as e:
            text = f"[خطای شناسایی: {e}]"
        except Exception as e:
            text = f"[خطای پردازش فایل: {e}]"

        speaker = f.split()[0]  # AI یا USER
        full_text += f"{speaker.upper()}: {text}\n"

    return full_text.strip()

def create_temp_folder(base_path="temp"):
    folder_name = str(uuid.uuid4())
    path = os.path.join(base_path, folder_name)
    os.makedirs(path, exist_ok=True)
    return path

def resolve_call(transcript: str) -> dict:
    resolved = False
    reason = "هیچ نتیجه واضحی حاصل نشد یا کاندید گیج به نظر می‌رسید"
    return {"resolved": resolved, "reason": reason}

def analyze_call(transcript: str) -> dict:
    score = 7 
    summary = "تماس به‌خوبی پیش رفت و کاندید به طور مناسب مشارکت داشت."
    positives = []
    negatives = []
    return {"score": score, "summary": summary, "positives": positives, "negatives": negatives}

def decide_action(resolution: dict, analysis: dict) -> dict:
    if not resolution["resolved"]:
        return {
            "tool_name": "ارجاع به کارشناس انسانی",
            "arguments": {
                "priority": "بالا",
                "reason": resolution["reason"]
            }
        }
    return {
        "tool_name": "اقدام لازم انجام شد",
        "arguments": {
            "priority": "کم",
            "reason": "تماس بدون مشکل انجام شد"
        }
    }

def extra_insights(transcript: str) -> dict:
    confidence = 1
    hr_suggestion = "اسکریپت تماس فعلی مؤثر است"
    risk_flags = []
    sentiment = "مثبت"
    return {
        "confidence": confidence,
        "hr_suggestion": hr_suggestion,
        "risk_flags": risk_flags,
        "sentiment": sentiment
    }

@app.route("/upload_folder", methods=["POST"])
def upload_folder():
    if "files" not in request.files:
        raise AppError("هیچ فایلی ارسال نشده است")

    files = request.files.getlist("files")
    if not files:
        raise AppError("لیست فایل‌ها خالی است")

    temp_dir = create_temp_folder()  # ✅ بدون files

    for file in files:
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)

    transcript = transcribe_conversation(temp_dir)

    llm_result = evaluate_call_with_llm(transcript)

    return jsonify({
        "success": True,
        "transcript": transcript,
        **llm_result
    })

if __name__ == "__main__":
    app.run(debug=True)
