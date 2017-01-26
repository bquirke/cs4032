import json


from flask import Flask
from flask import request
from flask import jsonify
from flask import Response
from flask_pymongo import PyMongo
from pymongo import MongoClient
from Crypto.Cipher import AES
from serverSetup import Server
from serverSetup import AuthenticationLayer

SHARED_SERVER_KEY = 'fedcba0123456789abcdef9876543210'

application = Flask(__name__)
mongo = PyMongo(application)

'''with application.app_context():
    db = mongo.db
    db.clients.drop()
    db.servers.drop()
    db.publicKeys.drop()'''

# Setting up the database conn

#REDUNDANT
db_server = "localhost"
db_port = "27017"
connect_string = "mongodb://" + db_server + ":" + db_port

openConnection = MongoClient(connect_string)
db = openConnection.authenServer
clients = db.clients
'''db.clients.drop()
db.servers.drop()
db.publicKeys.drop()
db.directories.drop()
db.files.drop()'''



@application.route('/test', methods=['POST'])  # HTTP requests posted to this method
def test():
    print("Test Worked!!")
    return jsonify({'success': True})


@application.route('/createClient', methods=['POST'])  # Security needs to be looked at
def createClient():
    with application.app_context():
        client_data = request.get_json(force=True)
        client_id = client_data.get('client_id')
        public_key = AuthenticationLayer.getPublicKey(client_id)

        client_username = client_data.get('client_username')
        client_password = client_data.get('password')

        '''client_serverHost = client_data.get('server_host')
        client_serverPost = client_data.get('server_port')'''

        data = {"client_id": client_id,
                "username": client_username,
                "password": client_password,
                "public_key": public_key ,
                "session_key": "0000",   # Should be blank for now except for possibly automatic login after creation
                "server_host": "0000",
                "server_port": "0000"}  # Needs to be randomly generated

        dbInsert = db.clients.insert_one(data).inserted_id
        return jsonify({'success': True})


@application.route('/authClient', methods=['POST'])
def authenticateClient():
    client_data = request.get_json(force=True)
    client_id = client_data.get('client_id')
    client_pw = client_data.get('password')
    user = AuthenticationLayer.user_auth(client_id, client_pw)   # Call AuthenticationLayer
    if user:
        rsp_token = json.dumps({'session_key': user['session_key'],
                            'session_key_expires': user['session_key_expires'],
                            'server_host': "127.0.0.1",                             #user['server_host'],#Automatic Server Allocation should be implementated
                            'server_port': "8093",                                  #user['server_port'],
                            'ticket': str(AuthenticationLayer.encode(SHARED_SERVER_KEY, user['session_key']), 'utf-8')})

        return jsonify({'success': True, 'token': str(AuthenticationLayer.encode(user['public_key'], rsp_token), 'utf-8')})

    return jsonify({'success': False})



if __name__ == '__main__':
    application.run()
