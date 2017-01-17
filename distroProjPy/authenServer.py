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

application = Flask(__name__)
mongo = PyMongo(application)


@application.route('/test', methods=['POST'])
def test():
    print("Test Worked!!")
    return jsonify({'success': True})


if __name__ == '__main__':
    application.run()
