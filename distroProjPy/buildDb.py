import datetime
from Crypto.Cipher import AES
from pymongo import MongoClient


#application = Flask(__name__)
#mongo = PyMongo(application)

'''with application.app_context():
    db = mongo.db
    db.clients.drop()
    db.servers.drop()
    db.publicKeys.drop()
'''
db_server = "localhost"
db_port = "27017"
connect_string = "mongodb://" + db_server + ":" + db_port

openConnection = MongoClient(connect_string)
db = openConnection.authenServer

clients = db.clients


db.clients.drop()
db.servers.drop()
db.publicKeys.drop()
db.directories.drop()
db.files.drop()
#db = mongo.db


client_list = [{"client_id": "1",
                "session_key": "000",
                "session_key_expirary_date": (
                    datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 4)).strftime('%Y-%m-%d %H:%M:%S'),
                "password": "AAAbbb1234567890",
                "public_key": "01234567890123456789abcd",
                "server_host": "127.0.0.1",
                "server_port": "0000"},

               {"client_id": "21",
                "session_key": "000",
                "session_key_expirary_date": (
                    datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 4)).strftime('%Y-%m-%d %H:%M:%S'),
                "password": "aaaBBB1234567890",
                "public_key": "abcd01234567890123456789",
                "server_host": "127.0.0.1",
                "server_port": "0000"},

               {"client_id": "5",
                "session_key": "000",
                "session_key_expirary_date": (
                    datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 4)).strftime('%Y-%m-%d %H:%M:%S'),
                "password": "password12345678",
                "public_key": "isthissixteenbitslong123",
                "server_host": "127.0.0.1",
                "server_port": "0000"}
               ]

db.clients.insert(client_list)
###############################################



server_list = [{"reference": '1',"host": "127.0.0.1",
                "port": "8092",
                "is_master": True, "in_use": False},
               {"reference": '2',"host": "127.0.0.1",
                "port": "8093",
                "is_master": False, "in_use": False},
               {"reference": '3',"host": "127.0.0.1",
                "port": "8094",
                "is_master": False, "in_use": False}
               ]

db.servers.insert(server_list)
##############################################



keys_list = [{"public_key": '0123456789abcdef0123456789abcdef', "client_id": '4'},
             {"public_key": 'fedcba0123456789abcdef9876543210', "client_id": '2'},
             {"public_key": 'test', "client_id": '100'}]

db.publicKeys.insert(keys_list)
################################################

dir_list = [{"name": 'test'}]
db.directories.insert(dir_list)
''' Directory
    {"name": name
    , "reference": made from directory name
    , "server": server}'''

file_list = [{"name": 'test_file', "write_lock": False, 'write_lock_expires': 0000}]
db.files.insert(file_list)

''' File db setup
    {"name": name
    , "directory": directory_reference
    , "server": server_reference
    , "reference": reference made of directory name and directory ref
    , "updated_at": datetime.datetime.utcnow()
    , "file_text": file_text
     }'''
