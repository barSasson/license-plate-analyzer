import sys
import json
import logbook
from utils import is_url, request_with_retries

_logger = logbook.Logger(__name__)
OCR_TOKEN = "9fa66fa07388957"
OCR_ENGINE_URL = "https://api.ocr.space/parse/image"


class OCRFailure(Exception):
    reason = "OCR Engine failed to process your request"

    def __init__(self, info=None):
        self.info = info


class OCREngineFailure(OCRFailure):
    reason = "OCR engine failed to parse your image"


class OCRParsingFailure(OCRFailure):
    reason = "Failed to Parse OCR engine response"


class OCRInvalidFile(OCRFailure):
    reason = "Invalid File"


class InvalidPlateNumber(OCRFailure):
    reason = "Invalid plate number"


def pic_url_to_text(pic_url: str, language: str, api_key: str, **ocr_additonal_kwargs):
    api_kwargs = {'apikey': api_key, 'language': language, 'url': pic_url}
    api_kwargs.update(ocr_additonal_kwargs)
    return request_with_retries(OCR_ENGINE_URL, method="POST", data=api_kwargs)


def image_path_to_text(image_path: str, language: str, api_key: str, **ocr_additonal_kwargs):
    api_kwargs = {'apikey': api_key, 'language': language}
    api_kwargs.update(ocr_additonal_kwargs)

    try:
        with open(image_path, "rb") as file:
            return request_with_retries(OCR_ENGINE_URL, method="POST", data=api_kwargs, files={image_path: file})
    except (FileNotFoundError, IOError):
        orig_exc_info = sys.exc_info()
        _logger.debug(f"Invalid file {image_path}, exception: {orig_exc_info}")
        raise OCRInvalidFile(image_path)


def parse_engine_result(result):
    try:
        results = json.loads(result)
    except TypeError:
        _logger.debug(f"Json serialization failed on {result}")
        raise OCRParsingFailure(result)

    if "ParsedResults" not in results:
        _logger.debug(f"Could not find valid results from OCR engine, response={results}")
        raise OCREngineFailure(results)

    if not results["ParsedResults"] or "ParsedText" not in results["ParsedResults"][0]:
        _logger.debug(f"Could not parse result from OCR engine, response={results}")
        raise OCRParsingFailure(results)

    return results["ParsedResults"][0]["ParsedText"]


def pic_to_text(url_or_file: str, language: str = "eng", api_key: str = OCR_TOKEN, **ocr_additonal_kwargs):
    if is_url(url_or_file):
        result = pic_url_to_text(url_or_file, language, api_key, **ocr_additonal_kwargs)
    else:
        result = image_path_to_text(url_or_file, language, api_key, **ocr_additonal_kwargs)

    return parse_engine_result(result)


def is_valid_license(plate):
    contains_alpha = is_alpha(plate)
    only_upper = plate.isupper()

    if (contains_alpha and not only_upper) or len(plate) < 4:
        return False

    return True


def license_plate_image_to_text(raw_result):
    plates = [plate for plate in raw_result.strip("\r").split("\n") if is_valid_license(plate)]
    if not plates:
        raise InvalidPlateNumber(f"Invalid plate: {plates}\nRaw text is {raw_result}")

    return plates[0].strip()


def is_public_transportation(license_plate):
    return license_plate[-1] in ["G", "6"]


def is_military_or_law_enforcement(license_plate):
    return "L" in license_plate or "M" in license_plate


def is_alpha(license_plate):
    return any(char.isalpha() for char in license_plate)


def is_no_alpha(license_plate):
    return not is_alpha(license_plate)


def analyze_plate(parsed_license_plate):
    result_dict = {"license_plate": parsed_license_plate,
                   "is_public_transportation": is_public_transportation(parsed_license_plate),
                   "is_military_or_law_enforcement": is_military_or_law_enforcement(parsed_license_plate),
                   "has_no_letters": is_no_alpha(parsed_license_plate)}
    result_dict["is_allowed"] = not result_dict["is_public_transportation"] and not result_dict[
        "is_military_or_law_enforcement"] and not result_dict["has_no_letters"]
    return result_dict
