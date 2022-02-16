from flask import Flask, send_file, send_from_directory, Blueprint, request
import json

@html.route('/')
    def index():
        return html.send_static_file("index.html")

@html.route('/textbox', methods=(["get"]))
    def textbox():
        text = request.args.get("text")
        with open('db.txt') as f:
            f.writelines(text)
        return json.dumps({'status'; 'sucess'})

@html.route('/printfile', methods=(['post']))
    def printfile():
        jstring = {}
        with open('db.txt') as f:
            jstring['text'] = f.read()
        return json.dumps(jstring)
 
