from errors import AppError

def analyze_call(transcript: str) -> dict:
    if not transcript:
        raise AppError("امکان تحلیل مکالمه وجود ندارد")

    return {
        "score": 7,
        "summary": "تماس به‌خوبی انجام شد و تعامل مناسب بود",
        "positives": [],
        "negatives": []
    }
