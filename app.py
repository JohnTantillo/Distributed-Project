# Author: John Tantillo
# To run: In one terminal run "npm run build" then "npm start". Make sure you are located in the /frontend directory
# In another terminal in the same level as the Dockerfile run "docker build -t project ." then "docker run -dp 5000:5000 project"
# After this, navigate to localhost:5000
#841jTjrC31zPVJLj
#486mongo
from flask import Flask, send_file, send_from_directory, Blueprint, request, render_template
import pymongo
import os
import json

app = Flask(__name__, static_url_path='', static_folder='frontend/build')
client = pymongo.MongoClient("mongodb+srv://486mongo:841jTjrC31zPVJLj@cluster0.8ym8n.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
#client = pymongo.MongoClient('localhost')
db = client['486db']
col = db['games']

@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/textbox', methods=(["post"]))
def textbox():
    text = request.form['writer']
    if text == "":
        return send_from_directory(app.static_folder, 'index.html')
    inserted = col.insert_one({"game": text})
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/printfile', methods=(['post']))
def printfile():
    all_games = col.find()
    game_col = []
    for game in all_games:
        game_col.append(game['game'])
    return render_template('index2.html', data=game_col)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
