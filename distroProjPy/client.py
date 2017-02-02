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
unencrypted_password1 = 'youWillNeverGues'
unencrypted_password2 = 'aaaaaaaaaaaaaaaa'


file_name = 'test_file_name.txt'
edited_file= 'edit_file_contents.txt'




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

def retrieve_client_info(response_text):
    encoded_token = json.loads(response_text)["token"]
    decoded = decode(keyDerivedFromPassword, encoded_token)
    decoded_data = json.loads(str(decoded, 'utf-8').strip())
    print("DECODED CLIENT AUTHENTICATION")
    client_data = {}

    client_data["session_key"] = decoded_data["session_key"]
    print("Session key for this client: " + client_data['session_key'])
    client_data['ticket'] = decoded_data["ticket"]
    client_data['server_host'] = decoded_data["server_host"]
    client_data['server_port'] = decoded_data["server_port"]

    print("Server host: " + client_data['server_host'])
    print("Server port: " + client_data['server_port'])

    return client_data



encrypted_password = str(encode(keyDerivedFromPassword, unencrypted_password1), 'utf-8')
encrypted_password2 = str(encode(keyDerivedFromPassword, unencrypted_password2), 'utf-8')
print(encrypted_password)


headers = {'Content-type': 'application/json'}

payload = {'client_id':'4','client_username': 'bryan', 'password': unencrypted_password1,
           "server_host": "127.0.0.1","server_port": "8093"}



# ADDING CLIENT
clientAdd1 = requests.post("http://127.0.0.1:5000/createClient", data=json.dumps(payload), headers=headers)
print (clientAdd1)
#time.sleep(3)

payload = {'client_id':'4','client_username': 'bryan', 'password': encrypted_password}

#AUTHORISING ADDED CLIENT
clientAuth1 = requests.post("http://127.0.0.1:5000/authClient", data=json.dumps(payload), headers=headers)
print(clientAuth1)
#time.sleep(3)

######### Client number 2 add and auth
payload2 = {'client_id':'1000','client_username': 'toshiba', 'password': unencrypted_password2,
           "server_host": "127.0.0.1","server_port": "8094"}

clientAdd2 = requests.post("http://127.0.0.1:5000/createClient", data=json.dumps(payload2), headers=headers)
print (clientAdd2)

payload2 = {'client_id':'1000','client_username': 'toshiba', 'password': encrypted_password2}
clientAuth2 = requests.post("http://127.0.0.1:5000/authClient", data=json.dumps(payload2), headers=headers)
print(clientAuth2)


#DECODING RESPONSE
response_text = clientAuth1.text
client1 = retrieve_client_info(response_text)

response_text = clientAuth2.text
client2 = retrieve_client_info(response_text)

###### SESSION KEY IS USED FROM NOW ON TO ENCRYPT MESSAGES BETWEEN SERVER AND CLIENT

###### FILE UPLOAD
fileDir = os.path.dirname(os.path.realpath('__file__'))
filePath = os.path.join(fileDir, 'client_files/' + file_name)
f = open(filePath)  # open a file
text = f.read()    # read the entire contents, should be UTF-8 text


enc_directory = str(encode(client1['session_key'], "/test"), "utf-8")
enc_file_name = str(encode(client1['session_key'], 'test_file_name.txt'), "utf-8")
enc_text = str(encode(client1['session_key'], text), "utf-8")

payload = {"directory_name" : enc_directory,"file_name": enc_file_name, "file_text": enc_text, "ticket": client1['ticket']}
url = "http://" + client1['server_host']+":" + client1['server_port']
fileUpload = requests.post(url + "/server/directory/file/upload", data=json.dumps(payload), headers=headers)
print(fileUpload)
time.sleep(5)


###### SAME FILE DOWNLOAD
payload = {"directory_name" : enc_directory,"file_name": enc_file_name,"ticket": client1['ticket'], 'aqquire-wite_lock': False}
fileDownload = requests.post(url + "/server/directory/file/download", data=json.dumps(payload), headers=headers)
print("recieved file from server -> " + fileDownload.text)

'''
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
'''
time.sleep(3)

###### SAME FILE DELETION
fileDeletion = requests.post(url + "/server/directory/file/delete", data=json.dumps(payload), headers=headers)
print(fileDeletion.content)

print("\n\n\n***************Beginning locking test***************")

time.sleep(5)

payload = {"directory_name" : enc_directory,"file_name": enc_file_name, "file_text": enc_text, "ticket": client1['ticket']}
url = "http://" + client1['server_host']+":" + client1['server_port']
fileUpload = requests.post(url + "/server/directory/file/upload", data=json.dumps(payload), headers=headers)
print("Uploaded file")
time.sleep(2)

payload = {"directory_name" : enc_directory,"file_name": enc_file_name,"ticket": client1['ticket'], 'aqquire-wite_lock': True}
fileDownload = requests.post(url + "/server/directory/file/download", data=json.dumps(payload), headers=headers)
print("recieved file from server -> " + fileDownload.text)
print("Client 1 aqquired file lock")
print("client 2 will attempt to download")
time.sleep(2)

## Client 2 attempted download
enc_directory2 = str(encode(client2['session_key'], "/test"), "utf-8")
enc_file_name2 = str(encode(client2['session_key'], 'test_file_name.txt'), "utf-8")

payload = {"directory_name" : enc_directory2,"file_name": enc_file_name2,"ticket": client2['ticket'], 'aqquire-wite_lock': False}
url2 = "http://" + client2['server_host']+":" + client2['server_port']
fileDownload = requests.post(url2 + "/server/directory/file/download", data=json.dumps(payload), headers=headers)
print("Client 2 told -> " + fileDownload.text)
time.sleep(2)


## Client 1 to upload edited file
fileDir = os.path.dirname(os.path.realpath('__file__'))
filePath = os.path.join(fileDir, 'client_files/' + edited_file)
f = open(filePath)  # open a file
text = f.read()    # read the entire contents, should be UTF-8 text
enc_text = str(encode(client1['session_key'], text), "utf-8")


payload = {"directory_name" : enc_directory,"file_name": enc_file_name, "file_text": enc_text, "ticket": client1['ticket']
           ,'count':0}
fileEditUpload = requests.post(url + "/server/directory/file/edit", data=json.dumps(payload), headers=headers)
print("Client 1 told after edit -> " + fileEditUpload.text)

payload = {"directory_name" : enc_directory,"file_name": enc_file_name,"ticket": client1['ticket'], 'aqquire-wite_lock': False}
fileDownload = requests.post(url + "/server/directory/file/download", data=json.dumps(payload), headers=headers)
print("Client 1 recieved file from server -> " + fileDownload.text)
time.sleep(2)

print("Client 1 will attempt to give up its lock")
time.sleep(1)
payload = {"directory_name" : enc_directory,"file_name": enc_file_name,"ticket": client1['ticket'], 'count': 0}
fileDownload = requests.post(url + "/server/directory/file/unlockFile", data=json.dumps(payload), headers=headers)
print("Client 1 recieved file from server -> " + fileDownload.text)

