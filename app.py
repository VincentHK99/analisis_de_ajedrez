from flask import Flask, render_template, request
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import pandas as pd
import functions

#initialize app
app = Flask(__name__)

#use functions from the functions.py file to source and clean game data
# to speed up development I read in a csv file instead of calling api as done below:
# game_data = functions.full_game_data('VincentHK99')

game_data = pd.read_csv('example_data.csv')

for i in game_data.columns:
  if is_datetime(game_data[i]) == True:
    game_data[i] = (pd.to_datetime(game_data[i]) - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')




@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analisis_del_juego")
def analisis_del_juego():
    return render_template("analisis_del_juego.html",data=game_data)


@app.route("/mis_estadisticas",methods=['POST','GET'])
def mis_estadisticas():
    if request.method == 'POST':
        time_control = request.form.get('time_control')
        print(time_control)
        results = functions.game_results(game_data,time_control=time_control,colour=0)
    else:
        time_control = '900+10'
        results = functions.game_results(game_data,time_control=time_control,colour=0)
    
    return render_template("mis_estadisticas.html",data=results,opening_data=functions.opening_sum(game_data,90))
