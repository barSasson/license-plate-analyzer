# Parking Lot License Plate Selector

This project includes backend and frontend for license plate analyzer to determine 
if the vehicle may enter the parking lot.
This service receives an image - either as a URL or a local path provided by a CLI.
The service will analyze the image and return a response whether the plate has past the criteria or not and will write
 the result to a local databse.


## Quick Start

Create a python 3 virtualenv and activate it
```
virtualenv -p python3 ./venv
source /path/to/your/venv/bin/activate
```
Install all the packages provided by requirements.txt, simply by running
```
pip install -r ./requirements.txt
```
In order to run the Flask App, please run:
```
export FLASK_APP=/path/to/project/parking_lot_gate/application.py
flask run
```
Once the backend service is up and running, you now can send requests using the CLI:
```
python /path/to_project/parking_lot_gate/frontend.py  --file_or_url   https://i.pinimg.com/originals/d0/0e/34/d00e3442b6c9c92b8cd594d981c6088a.jpg
```
