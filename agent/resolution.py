from errors import AppError

def resolve_call(transcript: str) -> dict:
    if not transcript:
        raise AppError("متن مکالمه خالی است")

    return {
        "resolved": False,
        "reason": "نتیجه مشخصی از تماس حاصل نشد"
    }
