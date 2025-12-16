import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY در فایل .env تنظیم نشده")

client = OpenAI(
    api_key=OPENAI_API_KEY,
)

SYSTEM_PROMPT = """
تو یک سیستم ارزیابی تماس هستی.
بر اساس متن مکالمه، کیفیت تماس را تحلیل کن و فقط خروجی ساختاریافته بده.
"""

CALL_EVALUATION_SCHEMA = {
    "name": "evaluate_call",
    "description": "تحلیل کیفیت تماس تلفنی",
    "parameters": {
        "type": "object",
        "properties": {
            "score": {
                "type": "number",
                "description": "امتیاز کلی تماس از 0 تا 5"
            },
            "summary": {
                "type": "string",
                "description": "خلاصه تحلیل تماس"
            },
            "strengths": {
                "type": "array",
                "items": {"type": "string"}
            },
            "weaknesses": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["score", "summary"]
    }
}

def evaluate_call_with_llm(transcript: str) -> dict:
    if not transcript or not transcript.strip():
        return {
            "success": False,
            "error": "متن مکالمه برای تحلیل وجود ندارد"
        }

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcript}
            ],
            functions=[CALL_EVALUATION_SCHEMA],
            function_call={"name": "evaluate_call"},
            temperature=0.2
        )

        message = response.choices[0].message
        print("LLM MESSAGE 👉", message)

        if not message.function_call:
            return {
                "success": False,
                "error": "مدل خروجی ساختاریافته تولید نکرد"
            }

        args_str = message.function_call.arguments
        args = json.loads(args_str)

        return {
            "success": True,
            "data": args
        }

    except json.JSONDecodeError as e:
        print("JSON PARSE ERROR 👉", e)
        return {
            "success": False,
            "error": "خروجی مدل JSON معتبر نیست"
        }

    except Exception as e:
        print("LLM ERROR 👉", e)
        return {
            "success": False,
            "error": str(e)
        }
