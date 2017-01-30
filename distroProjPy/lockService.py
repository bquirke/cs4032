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
from serverSetup import File

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

    def write_lock_aqquire(file_name, directory_name, session_key):
        file_data = db.files.find_one({"name": file_name, "directory": directory_name})

        if file_data["write_lock"] == True:
            return jsonify({'success': False, 'text': 'File already has a write_lock. Try again later'})

        else:
            write_lock_expire = session_key_expires = (datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60)).strftime(
                '%Y-%m-%d %H:%M:%S')    # Some arbitary time
            file_data["write_lock"] = True
            file_data["write_lock_expires"] = write_lock_expire
            file_data["lock_user_key"] = session_key
            if (File.update_file(file_name, directory_name, file_data)):
                return jsonify({"success": True, 'data': file_data})


    def check_write_lock(file_name, directory_name):
        file_data = db.files.find_one({"name": file_name, "directory": directory_name})

        if file_data["write_lock"] == True:
            return jsonify({'success': False, 'text': 'File has a write_lock. Try again later'})

    def unlock(file_name, directory_name, session_key):
        file_data = db.files.find_one({"name": file_name, "directory": directory_name, "lock_user_key": session_key})

        if file_data:
            if file_data["write_lock"] == True:
                file_data["write_lock"] = False
                if (File.update_file(file_name, directory_name, file_data)):
                    return jsonify({"success": True, 'text': file_data})    # FILE UNLOCKED
                else: return jsonify({"success": False, 'text': "ERROR when updating file lock"})

            else: return jsonify({"success": True, 'text': "File already unlocked"})

        else:
            return jsonify({"success": False, 'text': "No file with searched data exits"})