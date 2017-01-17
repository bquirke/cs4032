import requests
import base64
import json
import hashlib
import datetime
from Crypto.Cipher import AES
from pymongo import MongoClient

db_server = "localhost"
db_port = "27017"
connect_string = "mongodb://" + db_server + ":" + db_port

openConnection = MongoClient(connect_string)
db = openConnection.distro

clients = db.clients
db.clients.drop()

client_list = [{"client_id": "1",
                "session_key": "000",
                "session_key_expirary_date": (
                    datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 4)).strftime('%Y-%m-%d %H:%M:%S'),
                "password": "AAAbbb1234567890",
                "public_key": "01234567890123456789abcd"},
               {"client_id": "21",
                "session_key": "000",
                "session_key_expirary_date": (
                    datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 4)).strftime('%Y-%m-%d %H:%M:%S'),
                "password": "aaaBBB1234567890",
                "public_key": "abcd01234567890123456789"},
               {"client_id": "5",
                "session_key": "000",
                "session_key_expirary_date": (
                    datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 4)).strftime('%Y-%m-%d %H:%M:%S'),
                "password": "password12345678",
                "public_key": "isthissixteenbitslong123"}
               ]

clients.insert(client_list)
