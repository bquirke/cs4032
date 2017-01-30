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


###########################################
class Server:
    def __init__(self):
        pass

    def get_servers():
        return db.servers.find()

    def create(host, port):

        insert = db.servers.insert_one({"host": host, "port": port})
        return insert

    def find_server(host, port):
        return db.servers.find({"host": host, "port": port})


#############################################
class AuthenticationLayer():
    def __init__(self):
        pass

    def pad(s):
        return s + " " * (AES.block_size - len(s) % AES.block_size)

    def encode(key, data):
        cipher = AES.new(key, AES.MODE_ECB)
        padded_data = AuthenticationLayer.pad(data)
        encrypted = base64.b64encode(cipher.encrypt(padded_data))
        return encrypted

    def decode(key, encrypted):
        cipher = AES.new(key, AES.MODE_ECB)
        decoded_data = cipher.decrypt(base64.b64decode(encrypted))
        return decoded_data.strip()  ### NEED TO TEST

    def get_client(client_id):

        return db.clients.find_one({"client_id": client_id})

    def update_client(client_id, data):

        return db.clients.update({"client_id": client_id}, data, upsert=True)

    def getPublicKey(client_id):

        key = db.publicKeys.find_one({"client_id": "4"})
        if key:
            return key['public_key']
        return key

    def user_auth(client_id, encrypted_pw):
        client_data = AuthenticationLayer.get_client(client_id)
        byte_enc_pw = bytes(encrypted_pw, 'utf-8')
        print(client_data['public_key'])
        publicKey = client_data['public_key']
        decoded_password = AuthenticationLayer.decode(publicKey, byte_enc_pw)
        str_decoded_password = str(decoded_password, 'utf-8')

        if (str_decoded_password == client_data[
            'password']):  # If authorised client generate key and expirary date + update client
            session_key = ''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))

            session_key_expires = (datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 4)).strftime(
                '%Y-%m-%d %H:%M:%S')

            print(session_key)
            client_data['session_key'] = session_key
            client_data['session_key_expires'] = session_key_expires
            if (AuthenticationLayer.update_client(client_id, client_data)):
                return client_data
            else:
                return False

        else:
            return False


####################################################
class File:
    def __init__(self):
        pass

    def create(name, directory_name, directory_reference, server_reference, file_text):

        hex = hashlib.md5()
        print(type(directory_name))
        print(type(directory_reference))
        hex.update(bytes(directory_reference + "/", "utf-8") + directory_name)
        db.files.insert({"name": name, "directory": directory_reference
                         , "server": server_reference
                         , "reference": hex.hexdigest()
                         , "updated_at": datetime.datetime.utcnow()
                         , "file_text": file_text
                         , "write_lock": False,
                         'write_lock_expires': 0000
                         })
        file = db.files.find_one({"reference": hex.hexdigest()})
        return file

    def update_file(file_name, directory_name, data):
        return db.clients.update({"name": file_name, "directory": directory_name}, data, upsert=True)


#####################################################
class Directory:
    def __init__(self):
        pass

    def create(name, server):

        hex = hashlib.md5()
        hex.update(name)
        db.directories.insert({"name": name
                                  , "reference": hex.hexdigest()
                                  , "server": server})
        directory = db.directories.find_one({"name": name, "reference": hex.hexdigest()})
        return directory

    def isDirectories(name, reference, server_ref):

        try:
            if db.directories.find_one({"name": name, "reference": reference, "server": server_ref}):
                return True
        except:
            return False  # None type returned
