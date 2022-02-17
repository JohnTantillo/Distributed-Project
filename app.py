from flask import Flask, send_file, send_from_directory, Blueprint, request, render_template
from pymongo import MongoClient
import os
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/textbox', methods=(["post"]))
def textbox():
    text = request.form['textq']
    with open('db.txt', 'w') as f: # This is going to be changed to database
        f.write(str(text))
    return render_template('index.html')

@app.route('/printfile', methods=(['post']))
def printfile():
    jstring = {}
    with open('db.txt') as f: #This is going to be changed to data base
        jstring['text'] = f.read()
    return json.dumps(jstring)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
