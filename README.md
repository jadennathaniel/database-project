# create virtual environment and activate it
python3 -m venv env
source env/bin/activate

# install dependencies
pip install Flask mysql-connector-python

# run the app
python3 app.py