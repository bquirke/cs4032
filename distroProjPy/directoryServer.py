import json
import hashlib
import os
import threading
import requests


import flask
from flask import request
from flask import jsonify
from flask import Flask

from pymongo import MongoClient
from flask_pymongo import PyMongo

from serverSetup import File
from serverSetup import Directory
from serverSetup import AuthenticationLayer
from lockService import Lock

#from authenServer import application    # Not sure how feasible this is
#from authenServer import mongo
SHARED_SERVER_KEY = 'fedcba0123456789abcdef9876543210'

application = Flask(__name__)
mongo = PyMongo(application)

mongo_server = "127.0.0.1"
mongo_port = "27017"
connect_string = "mongodb://" + mongo_server + ":" + mongo_port

openConnection = MongoClient(connect_string)
db = openConnection.authenServer

CURRENT_HOST = None
CURRENT_PORT = None


def currentServer():
    servers = db.servers.find()
    for server in servers:
        if ((server['host'] == CURRENT_HOST) & (server['port'] == CURRENT_PORT)):
            return server

''' REPLICATION IMLEMENTATION

'''
def sendToMaster(data, header, url):
    r = requests.post("http://127.0.0.1:8092" + url, data=json.dumps(data), headers=header)
    print("MASTER SERVER REPLIED " + r.text)

def replicateUpload(data, headers):
    with application.app_context():
        servers = db.servers.find()
        for server in servers:
            if server['is_master'] == False:
                host = server["host"]
                port = server["port"]
                if (host == CURRENT_HOST and port == CURRENT_PORT):
                    continue
                print("POSTING UPLOAD REQUEST TO " + server['port'])
                r = requests.post("http://" + host + ":" + port + "/server/directory/file/upload",
                                  data=json.dumps(data), headers=headers)
                print(r.text)


def replicateDelete(data, headers):
    with application.app_context():
        servers = db.servers.find()
        for server in servers:
            if server['is_master'] == False:
                host = server['host']
                port = server['port']
                if (host == CURRENT_HOST and port == CURRENT_PORT):
                    continue
                print("POSTING DELETE REQUEST TO " + server['port'])
                r = requests.post("http://" + host + ":" + port + "/server/directory/file/delete",
                                  data=json.dumps(data), headers=headers)
                print(r.text)

def replicateEdit(data, headers):
    with application.app_context():
        servers = db.servers.find()
        for server in servers:
            if server['is_master'] == False:
                host = server['host']
                port = server['port']
                if (host == CURRENT_HOST and port == CURRENT_PORT):
                    continue
                print("POSTING EDIT REQUEST TO " + server['port'])
                r = requests.post("http://" + host + ":" + port + "/server/directory/file/edit",
                                  data=json.dumps(data), headers=headers)
                print(r.text)

def replicateLockFile(data, headers):
    with application.app_context():
        servers = db.servers.find()
        for server in servers:
            #if server['is_master'] == False: REMOVED AS REPLICATING FROM WORKER SERVER FOR NOW
            host = server['host']
            port = server['port']
            if (host == CURRENT_HOST and port == CURRENT_PORT):
                continue
            print("POSTING LOCK FILE REQUEST TO " + server['port'])
            r = requests.post("http://" + host + ":" + port + "/server/directory/file/lockFile",
                              data=json.dumps(data), headers=headers)
            print(r.text)


def replicateUnlock(data, headers):
    with application.app_context():
        servers = db.servers.find()
        for server in servers:
            #if server['is_master'] == False: REMOVED AS REPLICATING FROM WORKER SERVER FOR NOW
            host = server['host']
            port = server['port']
            if (host == CURRENT_HOST and port == CURRENT_PORT):
                continue
            print("POSTING LOCK FILE REQUEST TO " + server['port'])
            r = requests.post("http://" + host + ":" + port + "/server/directory/file/unlockFile",
                              data=json.dumps(data), headers=headers)
            print(r.text)


def retrieve_file(file_name, directory_name):
    hex = hashlib.md5()
    hex.update(directory_name)
    server = currentServer()

    dir = db.directories.find_one({"name": directory_name, "reference": hex.hexdigest(), "server": server["reference"]})

    if not dir:
        print("NO DIRECTORY FOUND")
        return jsonify({'success': False, 'message': "NO DIRECTORY FOUND"})

    file = db.files.find_one({"name": file_name, "server": server["reference"], "directory": dir["reference"]})

    if not file:
        print("NO FILE FOUND")
        return jsonify({'success': False, 'message': "NO FILE FOUND"})

    print("SENDING FILE -> " + str(file_name, "utf-8"))
    path = server['reference']
    return flask.send_file(os.path.join(path, file['reference']))


''' DFS STANDARD INFASTRUCTURE

'''
@application.route('/server/directory/file/lockFile', methods=['POST'])
def lock_file():
    headers = request.headers
    data = request.get_json(force=True)
    ticket = data['ticket']
    decoded_ticket = AuthenticationLayer.decode(SHARED_SERVER_KEY, bytes(ticket, 'utf-8'))

    file_name = AuthenticationLayer.decode(decoded_ticket, bytes(data['file_name'], "utf-8"))
    directory_name = AuthenticationLayer.decode(decoded_ticket, bytes(data['directory_name'], "utf-8"))
    server = currentServer()

    if data['aqquire-wite_lock'] == True:
        locking = Lock.write_lock_aqquire(file_name, directory_name, decoded_ticket, server)

        if locking['success'] == True:
            # Propagate write_lock to other services
            return retrieve_file(file_name, directory_name) #Obtained write lock

        else:
            return jsonify(locking)  # Error

@application.route('/server/directory/file/unlockFile', methods=['POST'])
def unlock_file():
    path_url = '/server/directory/file/unlockFile'
    headers = request.headers
    data = request.get_json(force=True)
    ticket = data['ticket']
    decoded_ticket = AuthenticationLayer.decode(SHARED_SERVER_KEY, bytes(ticket, 'utf-8'))

    file_name = AuthenticationLayer.decode(decoded_ticket, bytes(data['file_name'], "utf-8"))
    directory_name = AuthenticationLayer.decode(decoded_ticket, bytes(data['directory_name'], "utf-8"))
    server = currentServer()
    count = data['count']

    unlock_file = Lock.unlock(file_name,directory_name, decoded_ticket, server)

    if unlock_file["success"] == True:  #file unlocked
        ####REPLICATION
        if (server["is_master"]):
            thr = threading.Thread(target=replicateUnlock, args=(data, headers), kwargs={})
            thr.start()

        elif count == 0:  # Count is to stop recursively calling the replication of transaction
            count += 1
            data['count'] = count
            headers = request.headers
            # url = "http://" + server['host']+":" + server['port'] + path_url
            sendToMaster(data, headers, path_url)

        return jsonify(unlock_file)

    else:
        return jsonify(unlock_file)



@application.route('/server/directory/file/upload', methods=['POST'])  # HTTP requests posted to this method
def file_upload():
    path_url = '/server/directory/file/upload'
    headers = request.headers
    file_msg = request.get_json(force=True)
    ticket = file_msg['ticket']
    decoded_ticket = AuthenticationLayer.decode(SHARED_SERVER_KEY, bytes(ticket, "utf-8"))

    file_name = AuthenticationLayer.decode(decoded_ticket, bytes(file_msg['file_name'], "utf-8"))
    directory_name = AuthenticationLayer.decode(decoded_ticket, bytes(file_msg['directory_name'], "utf-8"))
    file_text = AuthenticationLayer.decode(decoded_ticket, bytes(file_msg['file_text'], "utf-8"))

    hex = hashlib.md5()
    hex.update(directory_name)
    server = currentServer()

    if not db.directories.find_one({"name": directory_name, "reference": hex.hexdigest(), "server": server["reference"]}):
        directory = Directory.create(directory_name, server["reference"])   # Create a new directory
        print("DIRECTORY CREATED -> " + str(directory_name, "utf-8"))

    else:
        directory = db.directories.find_one({"name": directory_name, "reference": hex.hexdigest(), "server": server["reference"]})

    if not db.files.find_one({"name": file_name, "server": server["reference"], "directory": directory["reference"]}):
        file = File.create(file_name, directory_name, directory["reference"], server["reference"], file_text )
        print("FILE CREATED -> " + str(file_name, "utf-8") )

    else:
        #file = db.files.find_one({"name": file_name, "server": server["reference"], "directory": directory["reference"]})
        return jsonify({'success': False, 'text': 'File already exists'})   # Does not cater for edit


    # Writing to disk
    path = server['reference']
    if not os.path.exists(path):
        os.makedirs(path)

    with open(os.path.join(path, file['reference']), 'wb') as fo:
        fo.write(file_text)         #Store it for flask


    ####REPLICATION
    if (server["is_master"]):
        thr = threading.Thread(target=replicateUpload, args=(file_msg, headers), kwargs={})
        thr.start()
    else:
        headers = request.headers
        #url = "http://" + server['host']+":" + server['port'] + path_url
        sendToMaster(file_msg, headers, path_url)

    return jsonify({'success': True})



@application.route('/server/directory/file/download', methods=['POST'])
def file_download():
    path_url = '/server/directory/file/download'
    headers = request.headers
    data = request.get_json(force=True)
    ticket = data['ticket']
    decoded_ticket = AuthenticationLayer.decode(SHARED_SERVER_KEY, bytes(ticket, 'utf-8'))

    file_name = AuthenticationLayer.decode(decoded_ticket, bytes(data['file_name'], "utf-8"))
    directory_name = AuthenticationLayer.decode(decoded_ticket, bytes(data['directory_name'], "utf-8"))
    server = currentServer()

    if data['aqquire-wite_lock'] == True:
        locking = Lock.write_lock_aqquire(file_name, directory_name, decoded_ticket, server)

        if locking['success'] == True:
            # Propagate write_lock to other services
            replicateLockFile(data,headers) # Non threaded for the moment
            return retrieve_file(file_name, directory_name) #Obtained write lock

        else:
            return jsonify(locking)  # Error

    else:   # Do not want write_lock (read lock) but must check write lock
        locking = Lock.check_write_lock(file_name,directory_name, server, decoded_ticket)

        if locking['success'] == True: # File is locked
            return jsonify(locking)

        elif (locking['success'] == False) and (locking['text'] == 'None type returned'): # Retrieval error
            return jsonify(locking)

        elif locking['success'] == False: # File is unlocked
            return retrieve_file(file_name,directory_name)

@application.route('/server/directory/file/delete', methods=['POST'])
def file_delete():
    path_url = '/server/directory/file/delete'
    headers = request.headers
    data = request.get_json(force=True)
    ticket = data['ticket']
    decoded_ticket = AuthenticationLayer.decode(SHARED_SERVER_KEY, bytes(ticket, 'utf-8'))

    file_name = AuthenticationLayer.decode(decoded_ticket, bytes(data['file_name'], "utf-8"))
    directory_name = AuthenticationLayer.decode(decoded_ticket, bytes(data['directory_name'], "utf-8"))

    hex = hashlib.md5()
    hex.update(directory_name)
    server = currentServer()

    dir = db.directories.find_one({"name": directory_name, "reference": hex.hexdigest(), "server": server["reference"]})

    if not dir:
        return jsonify({'success': False, 'message': "NO DIRECTORY OF THAT NAME FOUND"})

    file = db.files.find_one({"name": file_name, "server": server["reference"], "directory": dir["reference"]})

    if not file:
        return jsonify({'success': False, 'message': "NO FILE OF THAT NAME FOUND"})

    path = server['reference']
    os.remove(os.path.join(path, file['reference']))

    delete_file = db.files.delete_one({"name": file_name, "server": server["reference"], "directory": dir["reference"]})
    if not delete_file.deleted_count >= 0:
        return jsonify({'success': False})

    print("FILE DELETED -> " + str(file_name, "utf-8"))

    # Send the file to the master server to be broadcast from there
    if (server["is_master"]):
        thr = threading.Thread(target=replicateDelete, args=(data, headers), kwargs={})
        thr.start()

    else:
        # We are the master server so call our replicate function
        headers = request.headers
        #url = "http://" + server['host']+":" + server['port'] + path_url
        print("SENDING MASTER URL PATH -> " + path_url)
        sendToMaster(data, headers, path_url)


    return jsonify({'success': True})


@application.route('/server/directory/file/edit', methods=['POST'])  # HTTP requests posted to this method
def file_edit():
    path_url = '/server/directory/file/edit'
    headers = request.headers
    file_msg = request.get_json(force=True)
    ticket = file_msg['ticket']
    decoded_ticket = AuthenticationLayer.decode(SHARED_SERVER_KEY, bytes(ticket, "utf-8"))

    file_name = AuthenticationLayer.decode(decoded_ticket, bytes(file_msg['file_name'], "utf-8"))
    directory_name = AuthenticationLayer.decode(decoded_ticket, bytes(file_msg['directory_name'], "utf-8"))
    file_text = AuthenticationLayer.decode(decoded_ticket, bytes(file_msg['file_text'], "utf-8"))
    count = file_msg['count']

    hex = hashlib.md5()
    hex.update(directory_name)
    server = currentServer()

    dir = db.directories.find_one({"name": directory_name, "reference": hex.hexdigest(), "server": server["reference"]})

    if not dir:
        print("NO DIRECTORY FOUND")
        return jsonify({'success': False, 'message': "NO DIRECTORY FOUND"})

    file = db.files.find_one({"name": file_name, "server": server["reference"], "directory": dir["reference"]})

    if not file:
        print("NO FILE FOUND")
        return jsonify({'success': False, 'message': "NO FILE FOUND"})
    ########################################################################################

    file_lock = db.files.find_one({"name": file_name, "server": server["reference"], "directory": dir["reference"]
                                   ,'lock_user_key': decoded_ticket})
    if not file_lock:
        print("CLIENT DOES NOT OWN LOCK ON THIS FILE")
        return jsonify({'success': False, 'message': "YOU DO NOT HAVE LOCK FOR THIS FILE"})

    file['file_text'] = file_text
    file_status = File.update_file(file_name,dir, server, decoded_ticket, file) #Overwrite


    # Writing to disk
    path = server['reference']
    if not os.path.exists(path):
        os.makedirs(path)

    with open(os.path.join(path, file['reference']), 'wb') as fo:
        fo.write(file_text)  # Store it for flask

    ####REPLICATION
    if (server["is_master"]):
        thr = threading.Thread(target=replicateEdit, args=(file_msg, headers), kwargs={})
        thr.start()

    elif count == 0:    # Count is to stop recursively calling the replication of transaction
        count += 1
        file_msg['count'] = count
        headers = request.headers
        # url = "http://" + server['host']+":" + server['port'] + path_url
        sendToMaster(file_msg, headers, path_url)

    return jsonify({'success': True, 'text': "File edited and saved"})



if __name__ == '__main__':
    with application.app_context():
        servers = db.servers.find()
        for server in servers:
            print(server)
            print("\n")
            if ((server['in_use'] == False)):#& (server['is_master'] == False)): # Temporary to disable server 8092
                if server['is_master']:
                    print("\nIS MASTER SERVER\n")
                server['in_use'] = True
                CURRENT_HOST = server['host']
                CURRENT_PORT = server['port']
                db.servers.update({'reference': server['reference']}, server, upsert=True)
                application.run(host=server['host'], port=server['port'])