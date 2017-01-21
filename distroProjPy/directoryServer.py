import base64
import datetime
import json
import hashlib
import os
import threading
import requests
import random
import string

from flask import Flask
from flask import request
from flask import jsonify
from flask import Response
from flask_pymongo import PyMongo
from pymongo import MongoClient
from Crypto.Cipher import AES
from serverSetup import File
from serverSetup import Directory
from serverSetup import Server
from serverSetup import AuthenticationLayer

from authenServer import application    # Not sure how feasible this is
from authenServer import mongo
SHARED_SERVER_KEY = 'fedcba0123456789abcdef9876543210'

#application = Flask(__name__)
#mongo = PyMongo(application)

mongo_server = "127.0.0.1"
mongo_port = "27017"
connect_string = "mongodb://" + mongo_server + ":" + mongo_port

openConnection = MongoClient(connect_string)
db = openConnection.authenServer

CURRENT_HOST = None
CURRENT_PORT = None

def currentServer():
    servers = db.servers.find()
    for server in servers:
        if ((server['host'] == CURRENT_HOST) & (server['port'] == CURRENT_PORT)):
            return server




@application.route('/server/directory/file/upload', methods=['POST'])  # HTTP requests posted to this method
def file_upload():
    file_msg = request.get_json(force=True)
    ticket = file_msg['ticket']
    decoded_ticket = AuthenticationLayer.decode(SHARED_SERVER_KEY, bytes(ticket, "utf-8"))

    file_name = AuthenticationLayer.decode(decoded_ticket, bytes(file_msg['file_name'], "utf-8"))
    directory_name = AuthenticationLayer.decode(decoded_ticket, bytes(file_msg['directory_name'], "utf-8"))
    file_text = AuthenticationLayer.decode(decoded_ticket, bytes(file_msg['file_text'], "utf-8"))

    hex = hashlib.md5()
    hex.update(directory_name)
    server = currentServer()

    if not db.directories.find_one({"name": directory_name, "reference": hex.hexdigest(), "server": server["reference"]}):
        directory = Directory.create(directory_name, server["reference"])   # Create a new directory
        print("DIRECTORY CREATED")

    else:
        directory = db.directories.find_one({"name": directory_name, "reference": hex.hexdigest(), "server": server["reference"]})

    if not db.files.find_one({"name": file_name, "server": server["reference"], "directory": directory["reference"]}):
        file = File.create(file_name, directory_name, directory["reference"], server["reference"], file_text )

    else:
        file = db.files.find_one({"name": file_name, "server": server["reference"], "directory": directory["reference"]})

    #### IMPLEMNT REPLICATION

    return jsonify({'success': True})





@application.route('/server/directory/file/download', methods=['POST'])
def file_download():
    print("TEST")

''''@application.route('/server/directory/file/delete', methhods=['POST'])
def file_delete():
    print()'''



if __name__ == '__main__':
    with application.app_context():
        print("TEST")
        servers = mongo.db.servers.find()
        for server in servers:
            print(server)
            if ((server['in_use'] == False) & (server['is_master'] == False)): # Temporary to disable server 8092
                server['in_use'] = True
                CURRENT_HOST = server['host']
                CURRENT_PORT = server['port']
                db.servers.update({'reference': server['reference']}, server, upsert=True)
                application.run(host=server['host'], port=server['port'])