import logging
from flask import Flask, request, current_app
from werkzeug.exceptions import HTTPException
from database import ParkingLotLoggingDB
from license_plate_analyzer import license_plate_image_to_text, analyze_plate, OCRFailure, pic_to_text

DB_LOCAL_PATH = 'parking_lot.db'
entrance_logging_db = ParkingLotLoggingDB.from_file_path(DB_LOCAL_PATH)
app = Flask(__name__)


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e

    if isinstance(e, OCRFailure):
        message = f"Engine could not process your plate: {e.reason}\n{e.info}\nError: {str(e)}"
        response = current_app.response_class(message, mimetype="text/plain")
        response.status_code = 409
        return response
    response = current_app.response_class(f"Something went terribly wrong:\n {e}", mimetype="text/plain")
    response.status_code = 500
    return response


@app.route('/check_license_plate', methods=["POST"])
def check_license():
    img_url_or_pic = request.json.get("file_or_url", None)
    raw_result = pic_to_text(img_url_or_pic)
    app.logger.info(f"Raw result from OCR engine: {raw_result}")
    parsed_license_plate = license_plate_image_to_text(raw_result)
    app.logger.info(f"Parsed license plate: {parsed_license_plate}")
    result = analyze_plate(parsed_license_plate)
    app.logger.info(f"License plate analyze: {result}")
    entrance_logging_db.insert_car_entry(**result)

    return "Allowed" if result["is_allowed"] else "Forbidden"


if __name__ == '__main__':
    app.run()
    app.logger.setLevel(logging.DEBUG)



