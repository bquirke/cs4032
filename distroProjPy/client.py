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

from cacheService import Cache

from Crypto.Cipher import AES
from Crypto import Random


# PASSWORD ENCRYPTION
keyDerivedFromPassword = '0123456789abcdef0123456789abcdef'
unencrypted_password = 'youWillNeverGues'
file_name = 'test_file_name.txt'




def pad(s):
    return s + " " * (AES.block_size - len(s) % AES.block_size)


def encode(key, data):
    cipher = AES.new(key, AES.MODE_ECB)
    x = len(data)
    padded_data = pad(data)
    y = len(padded_data)
    encrypted = base64.b64encode(cipher.encrypt(padded_data))
    return encrypted


def decode(key, encrypted):
    cipher = AES.new(key, AES.MODE_ECB)
    decoded_data = cipher.decrypt(base64.b64decode(encrypted))
    return decoded_data.strip()  ### NEED TO TEST



encrypted_password = str(encode(keyDerivedFromPassword, unencrypted_password), 'utf-8')
print(encrypted_password)


headers = {'Content-type': 'application/json'}

payload = {'client_id':'4','client_username': 'bryan', 'password': unencrypted_password,
           "server_host": "127.0.0.1","server_port": "8093"}



# ADDING CLIENT
clientAdd = requests.post("http://127.0.0.1:5000/createClient", data=json.dumps(payload), headers=headers)
print (clientAdd)
#time.sleep(3)

payload = {'client_id':'4','client_username': 'bryan', 'password': encrypted_password}

#AUTHORISING ADDED CLIENT
clientAuth = requests.post("http://127.0.0.1:5000/authClient", data=json.dumps(payload), headers=headers)
print(clientAuth)
#time.sleep(3)


#DECODING RESPONSE
response_text = clientAuth.text
encoded_token = json.loads(response_text)["token"]
decoded = decode(keyDerivedFromPassword,encoded_token)
decoded_data = json.loads(str(decoded, 'utf-8').strip())
print("DECODED CLIENT AUTHENTICATION")

session_key = decoded_data["session_key"]
print("Session key for this client: " + session_key)
ticket = decoded_data["ticket"]
server_host = decoded_data["server_host"]
server_port = decoded_data["server_port"]

print("Server host: " + server_host)
print("Server port: " + server_port)

###### SESSION KEY IS USED FROM NOW ON TO ENCRYPT MESSAGES BETWEEN SERVER AND CLIENT

###### FILE UPLOAD
fileDir = os.path.dirname(os.path.realpath('__file__'))
filePath = os.path.join(fileDir, 'client_files/' + file_name)
f = open(filePath)  # open a file
text = f.read()    # read the entire contents, should be UTF-8 text


enc_directory = str(encode(session_key, "/test"), "utf-8")
enc_file_name = str(encode(session_key, 'test_file_name.txt'), "utf-8")
enc_text = str(encode(session_key, text), "utf-8")

payload = {"directory_name" : enc_directory,"file_name": enc_file_name, "file_text": enc_text, "ticket": ticket}
url = "http://" + server_host+":" + server_port
fileUpload = requests.post(url + "/server/directory/file/upload", data=json.dumps(payload), headers=headers)
print(fileUpload)
time.sleep(5)


###### SAME FILE DOWNLOAD
payload = {"directory_name" : enc_directory,"file_name": enc_file_name,"ticket": ticket}
fileDownload = requests.post(url + "/server/directory/file/download", data=json.dumps(payload), headers=headers)
print("recieved file from server -> " + fileDownload.text)


cache = Cache()
cache.create_cache()
cache.cache_obj(file_name, fileDownload.text)

if cache.check_cache(file_name):
    cachedFile = cache.get_cached(file_name)
    print("CACHED VERSION OF FILE ->" + cachedFile)

else:
    payload = {"directory_name": enc_directory, "file_name": enc_file_name, "ticket": ticket}
    url = "http://" + server_host + ":" + server_port
    fileUpload = requests.post(url + "/server/directory/file/download", data=json.dumps(payload), headers=headers)

time.sleep(3)

###### SAME FILE DELETION
fileDeletion = requests.post(url + "/server/directory/file/delete", data=json.dumps(payload), headers=headers)
#print(fileDeletion.content)
