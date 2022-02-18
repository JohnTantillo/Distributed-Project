# Author: John Tantillo
from flask import Flask, send_file, send_from_directory, Blueprint, request, render_template
from pymongo import MongoClient
import os
import json

app = Flask(__name__, static_url_path='', static_folder='frontend/build')

@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/textbox', methods=(["post"]))
def textbox():
    text = request.form['writer']
    if text == "":
        return send_from_directory(app.static_folder, 'index.html')
    with open('db.txt', 'a') as f: # This is going to be changed to database
        f.write(str(text) + "\n")
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/printfile', methods=(['post']))
def printfile():
    jstring = {}
    with open('db.txt') as f: #This is going to be changed to data base
        jstring['text'] = f.read().split('\n')
    return render_template('index2.html', data=jstring['text'])

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
