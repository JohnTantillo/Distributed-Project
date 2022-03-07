# Author: John Tantillo
# To run: In one terminal run "npm run build" then "npm start". Make sure you are located in the /frontend directory
# In another terminal in the same level as the Dockerfile run "docker build -t project ." then "docker run -dp 5000:5000 project"
# After this, navigate to localhost:5000
# For phase 2 run "docker compose up -d --scale app=3" to run 3 containers of this server (UPDATE THIS LATER)
from flask import Flask, send_file, send_from_directory, Blueprint, request, render_template
import pymongo
import os
import json
import socket
import requests

app = Flask(__name__, static_url_path='', static_folder='frontend/build')
client = pymongo.MongoClient("mongodb://mongo:27017")
client.test
db = client['486db']
leader_db = db['node1']
node2_db = db['node2']
node3_db = db['node3']
col = db['games']
node = ''

@app.route('/')
def home():
    requests.post('http://node1:5000/who_am_i/node2')
    requests.post('http://node2:5000/who_am_i/node3')
    requests.post('http://node:5000/who_am_i/node')
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/textbox', methods=(["post"]))
def textbox():
    text = request.form['writer']
    if text == "":
        return send_from_directory(app.static_folder, 'index.html')
    ack1 = json.loads(requests.post('http://node:5000/acknowledge').text)['ack']
    if ack1:
        leader_db.insert_one({"game": text})
    ack2 = json.loads(requests.post('http://node1:5000/acknowledge').text)['ack']
    if ack2:
        node2_db.insert_one({"game": text})
    ack3 = json.loads(requests.post('http://node2:5000/acknowledge').text)['ack']
    if ack3:
        node3_db.insert_one({"game": text})
    #leader_db.insert_one({"game": text})
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/printfile', methods=(['post']))
def printfile():
    if node == "node1":
        database = node2_db
    elif node == "node2":
        database = node3_db
    else:
        database = leader_db
    all_games = database.find()
    game_col = []
    for game in all_games:
        game_col.append(game['game'])
    return render_template('index2.html', data=game_col)

@app.route('/acknowledge', methods=(['post']))
def sendAck():
    return {'ack': True}

@app.route('/who_am_i/<name>', methods=(['post']))
def get_name(name):
    global node
    node = name
    return 

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
