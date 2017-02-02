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

    def write_lock_aqquire(file_name, directory_name, session_key, server):
        hex = hashlib.md5()
        hex.update(directory_name)
        # Find file
        dir = db.directories.find_one(
            {"name": directory_name, "reference": hex.hexdigest(), "server": server["reference"]})

        if not dir:
            print("NO DIRECTORY FOUND")
            result = {'success': False, 'message': "NO DIRECTORY FOUND"}
            return result

        file_data = db.files.find_one({"name": file_name, "server": server["reference"], "directory": dir["reference"]})

        if not file_data:
            print("NO FILE FOUND")
            result = {'success': False, 'message': "NO FILE FOUND"}
            return result

        ######################################################################################################
        #Locking stuff

        if file_data["write_lock"] == True:
            result = {'success': False, 'text': 'File already has a write_lock. Try again later'}
            return result

        else:
            write_lock_expire = session_key_expires = (datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60)).strftime(
                '%Y-%m-%d %H:%M:%S')    # Some arbitary time
            file_data["write_lock"] = True
            file_data["write_lock_expires"] = write_lock_expire
            file_data["lock_user_key"] = session_key
            if (File.update_file(file_name, dir, server, session_key, file_data)):
                result = {"success": True, 'data': file_data}
                return result


    def check_write_lock(file_name, directory_name, server, user_session_key):

        hex = hashlib.md5()
        hex.update(directory_name)
        # Find file
        dir = db.directories.find_one(
            {"name": directory_name, "reference": hex.hexdigest(), "server": server["reference"]})

        if not dir:
            print("NO DIRECTORY FOUND")
            result = {'success': False, 'text': "NO DIRECTORY FOUND"}
            return result

        file_data = db.files.find_one({"name": file_name, "server": server["reference"], "directory": dir["reference"]})

        if not file_data:
            print("NO FILE FOUND")
            result = {'success': False, 'text': "NO FILE FOUND"}
            return result

            ######################################################################################################
            # Locking stuff

        if file_data["write_lock"] == False:
            result = {'success': False, 'text': 'File unlocked'}
            return result

        elif file_data == None:
            result = {'success': False, 'text': 'None type returned'}
            return result

        elif file_data["write_lock"] == True and file_data['lock_user_key'] == user_session_key:
            result = {'success': False, 'text': 'Client owns lock. Allowed to dowload'}
            return result

        else:
            result = {'success': True, 'text': 'Could not download as file has a write_lock and is not owwned by user. Try again later'}
            return result

    def unlock(file_name, directory_name, session_key, server):
        hex = hashlib.md5()
        hex.update(directory_name)
        # Find file
        dir = db.directories.find_one(
            {"name": directory_name, "reference": hex.hexdigest(), "server": server["reference"]})

        if not dir:
            print("NO DIRECTORY FOUND")
            result = {'success': False, 'message': "NO DIRECTORY FOUND"}
            return result

        file_data = db.files.find_one({"name": file_name, "server": server["reference"], "directory": dir["reference"]
                                       , "lock_user_key": session_key})

        if not file_data:
            print("NO FILE FOUND")
            result = {'success': False, 'message': "NO FILE FOUND"}
            return result
            ######################################################################################################
            # Locking stuff

        if file_data:
            if file_data["write_lock"] == True:
                file_data["write_lock"] = False
                if (File.update_file(file_name, directory_name, file_data)):
                    result = {"success": True, 'text': file_data}    # FILE UNLOCKED
                    return result
                else:
                    result = {"success": False, 'text': "ERROR when updating file lock"}
                    return result

            else:
                result = {"success": True, 'text': "File already unlocked"}
                return result

        else:
            result = {"success": False, 'text': "No file with searched data exits"}
            return result
