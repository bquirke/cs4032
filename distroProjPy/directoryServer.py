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


#from authenServer import application
#from authenServer import mongo

application = Flask(__name__)
mongo = PyMongo(application)

mongo_server = "127.0.0.1"
mongo_port = "27017"
connect_string = "mongodb://" + mongo_server + ":" + mongo_port

openConnection = MongoClient(connect_string)
db = openConnection.authenServer



@application.route('/server/directory/file/upload', methods=['POST'])  # HTTP requests posted to this method
def file_upload():
    print()


@application.route('/server/directory/file/download', methods=['POST'])
def file_download():
    print("TEST")

'''@application.route('/server/directory/file/delete', methhods=['POST'])
def file_delete():
    print()'''



if __name__ == '__main__':
    with application.app_context():
        servers = db.servers.find()
        for server in servers:
            print(server)
            if (server['in_use'] == False):
                server['in_use'] = True
                db.servers.update({'reference': server['reference']}, server, upsert=True)
                application.run(host=server['host'], port=server['port'])