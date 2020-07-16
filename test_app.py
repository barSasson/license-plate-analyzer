import os
import pytest
from application import app

dir_path = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def client():
    return app.test_client()


@pytest.mark.parametrize("valid_plate", [
    "https://previews.123rf.com/images/grebeshkovmaxim/grebeshkovmaxim1906/grebeshkovmaxim190601096/"
    "124276526-number-plate-vehicle-registration-plates-of-portugal.jpg",
    f"{dir_path}/valid_plate.png"])
def test_allowed_plates(client, valid_plate):
    response = client.post("/check_license_plate", json={"file_or_url": valid_plate})
    assert response.status_code == 200
    assert response.data == b"Allowed"


@pytest.mark.parametrize("forbidden_plate", [
    f"{dir_path}/invalid_plate.jpg",
    "https://dor.mo.gov/motorv/images/BicentennialPlate-WebsiteGraphic.jpg",
    "https://i.pinimg.com/originals/d0/0e/34/d00e3442b6c9c92b8cd594d981c6088a.jpg"])
def test_forbidden_plates(client, forbidden_plate):
    response = client.post("/check_license_plate", json={"file_or_url": forbidden_plate})
    assert response.status_code == 200
    assert response.data == b"Forbidden"


@pytest.mark.parametrize("invalid_plate", [
    "https://i.ytimg.com/vi/MPV2METPeJU/maxresdefault.jpg"])
def test_invalid_plates(client, invalid_plate):
    response = client.post("/check_license_plate", json={"file_or_url": invalid_plate})
    assert response.status_code == 409
    assert "Engine could not process your plate: Invalid plate number" in str(response.data)
