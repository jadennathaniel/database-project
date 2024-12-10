# create virtual environment and activate it
python3 -m venv env
source env/bin/activate

# for Windows OS
python3 -m venv env
.\env\Scripts\Activate.ps1

# install dependencies
pip install Flask mysql-connector-python

# run the app
python3 app.py