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

collection = db.test_collection

post = {"author": "Hello",
			"date": datetime.datetime.utcnow()}

posts = db.posts
db.posts.drop()

post_id = posts.insert_one(post).inserted_id
print (post_id)
