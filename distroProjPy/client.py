import base64
import datetime
import json
import hashlib
import os
import threading
import requests
import time

from flask import Flask
from flask import request
from flask import jsonify
from flask import Response
from flask_pymongo import PyMongo
from pymongo import MongoClient

from Crypto.Cipher import AES
from Crypto import Random

publicKey = '0123456789abcdef0123456789abcdef'
unencrypted_password = 'youWillNeverGues'
cipher = AES.new(publicKey, AES.MODE_ECB)  # never use ECB in strong systems obviously
encrypted_password = str(base64.b64encode(cipher.encrypt(unencrypted_password)), 'utf-8')
print(encrypted_password)

print(len("0123456789abcdef0123456789abcdef"))

headers = {'Content-type': 'application/json'}

payload = {'client_id':'4','client_username': 'bryan', 'password': unencrypted_password,
           "server_host": "127.0.0.1","server_port": "0000"}

#TEST
#r = requests.post("http://127.0.0.1:5000/server/directory/file/download", data=json.dumps(payload), headers=headers)
#print(r)

clientAdd = requests.post("http://127.0.0.1:5000/createClient", data=json.dumps(payload), headers=headers)
print (clientAdd)
time.sleep(3)

payload = {'client_id':'4','client_username': 'bryan', 'password': encrypted_password}

clientAuth = requests.post("http://127.0.0.1:5000/authClient", data=json.dumps(payload), headers=headers)

response_text = clientAuth.text
encoded_token = json.loads(response_text)["token"]
decoded = cipher.decrypt(base64.b64decode(encoded_token))
decoded_data = json.loads(str(decoded, 'utf-8').strip())
print(decoded_data)
print("DECODED CLIENT AUTHENTICATION")

session_key = decoded_data["session_key"]
print(session_key)
ticket = decoded_data["ticket"]
server_host = decoded_data["server_host"]
server_port = decoded_data["server_port"]

# SESSION KEY IS USED FROM NOW ON TO ENCRYPT MESSAGES BETWEEN SERVER AND CLIENT



