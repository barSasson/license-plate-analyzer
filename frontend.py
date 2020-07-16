import click
import requests
APP_URL = "http://127.0.0.1:5000"


@click.command()
@click.option('--file_or_url', help='Local Filename or URL of license plate')
def check_plate(file_or_url):
    """CLI command that receives a license plate and returns wether it is allowed to enter the parking Lot"""
    print(requests.post(f"{APP_URL}/check_license_plate", json={"file_or_url": file_or_url}).content.decode())


if __name__ == '__main__':
    check_plate()
