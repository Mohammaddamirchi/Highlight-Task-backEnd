import os
import speech_recognition as sr
from errors import AppError

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

def transcribe_conversation(folder_path: str) -> str:
    if not os.path.exists(folder_path):
        raise AppError("پوشه فایل‌ها پیدا نشد", 404)

    recognizer = sr.Recognizer()
    files = os.listdir(folder_path)

    if not files:
        raise AppError("هیچ فایل صوتی‌ای ارسال نشده است")

    full_text = ""

    for f in sorted(files):
        if not f.lower().endswith(".wav"):
            continue

        file_path = os.path.join(folder_path, f)

        if os.path.getsize(file_path) > MAX_FILE_SIZE_BYTES:
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
        except sr.RequestError:
            raise AppError("سرویس تبدیل گفتار در دسترس نیست", 503)
        except Exception:
            raise AppError("خطا در پردازش فایل صوتی")

        speaker = f.split()[0].upper()
        full_text += f"{speaker}: {text}\n"

    if not full_text.strip():
        raise AppError("هیچ متنی از فایل‌ها استخراج نشد")

    return full_text.strip()
