from errors import AppError

def decide_action(resolution: dict, analysis: dict) -> dict:
    if not resolution or not analysis:
        raise AppError("اطلاعات کافی برای تصمیم‌گیری وجود ندارد")

    return {
        "tool_name": "ارجاع به کارشناس انسانی",
        "arguments": {
            "priority": "بالا",
            "reason": resolution.get("reason")
        }
    }
