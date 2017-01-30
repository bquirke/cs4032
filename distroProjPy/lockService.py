import base64
import datetime
import hashlib
import random
import string

from flask import Flask
from flask import request
from flask import jsonify
from flask_pymongo import PyMongo
from pymongo import MongoClient
from Crypto.Cipher import AES

application = Flask(__name__)
mongo = PyMongo(application)

mongo_server = "127.0.0.1"
mongo_port = "27017"
connect_string = "mongodb://" + mongo_server + ":" + mongo_port

openConnection = MongoClient(connect_string)
db = openConnection.authenServer


class Lock:
    def __init__(self):
        pass

    def write_lock_aqquire(self):
        print("To do")

    def check_write_lock(self):
        print("To do")

    def unlock(self):
        print("To do")