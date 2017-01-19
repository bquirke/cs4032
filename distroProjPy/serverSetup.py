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
from flask_pymongo import PyMongo
from Crypto.Cipher import AES


application = Flask(__name__)
mongo = PyMongo(application)


class Server:
    def __init__(self):
        pass

    def get_servers(self):
        return mongo.db.server.find()

    def create(host, port):
        db = mongo.db
        insert = db.servers.insert_one({"host": host, "port": port})


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
        db = mongo.db
        return db.clients.find_one({"client_id": client_id})

    def update_client(client_id, data):
        db = mongo.db
        return db.clients.update({"client_id": client_id}, data, upsert=True)

    def getPublicKey(client_id):
        db = mongo.db
        key = db.publicKeys.find_one({"client_id": "4"})
        if key:
            return key['public_key']
        return key

    def user_auth(client_id, encrypted_pw):
        client_data = AuthenticationLayer.get_client(client_id)
        byte_enc_pw = bytes(encrypted_pw, 'utf-8')
        publicKey = client_data['public_key']
        decoded_password = AuthenticationLayer.decode(publicKey,byte_enc_pw)
        str_decoded_password = str(decoded_password, 'utf-8')

        if (str_decoded_password == client_data['password']):
            session_key = ''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))

            session_key_expires = (datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 4)).strftime(
                '%Y-%m-%d %H:%M:%S')

            client_data['session_key'] = session_key
            client_data['session_key_expires'] = session_key_expires
            if (AuthenticationLayer.update_client(client_id, client_data)):
                return client_data
            else:
                return False

        else:
            return False
