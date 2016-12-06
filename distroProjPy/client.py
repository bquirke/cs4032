import base64
import datetime
import json 
import hashlib
import os
import threading
import requests

from flask import Flask
from flask import request
from flask import jsonify
from flask import Response
from flask_pymongo import PyMongo
from pymongo import MongoClient
from Crypto.Cipher import AES

headers = {'Content-type': 'application/json'}
payload = {'client_id': 2, 'encrypted_password': "chaps"}

r = requests.post("http://127.0.0.1:5000/test", data=json.dumps(payload), headers=headers)