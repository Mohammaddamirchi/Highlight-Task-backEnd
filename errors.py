from flask import jsonify

class AppError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

def handle_app_error(error):
    return jsonify({
        "success": False,
        "error": error.message
    }), error.status_code

def handle_unexpected_error(error):
    print(".")
    print(error)
    return jsonify({
        "success": False,
        "error": "خطای غیرمنتظره‌ای رخ داده است. لطفاً دوباره تلاش کنید."
    }), 500
