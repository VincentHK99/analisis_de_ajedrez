from flask import Flask, render_template
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import pandas as pd
import functions
import json

#initialize app
app = Flask(__name__)

#use functions from the functions.py file to source and clean game data
game_data = functions.full_game_data('VincentHK99')

for i in game_data.columns:
  if is_datetime(game_data[i]) == True:
    game_data[i] = (pd.to_datetime(game_data[i]) - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')


game_data = game_data.to_dict()

#convert the file into json format so it can be understood by javascript
game_data_json = json.dumps(game_data)


@app.route("/")
def index():
    return render_template("index.html",game_data_json=game_data_json)
