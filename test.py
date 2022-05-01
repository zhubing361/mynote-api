# coding:utf8
from pymongo import MongoClient
from pymongo.database import Database, Collection
import pymongo

from datetime import datetime

import time
print(datetime.today().timestamp())

print("now time:", time.time())

print("pymongo version:", pymongo.version)

created_at = 1651319745.273518
created_at = datetime.utcfromtimestamp(created_at+28800)
created_at_formated = created_at.strftime("%Y-%m-%d %H:%M:%S")
print("created_at_formated:" + created_at_formated)

MONGO_PORT = 30002
client = MongoClient(
    host='mongo_rs2',
    port=MONGO_PORT,
    document_class=dict,
    tz_aware=False,
    connect=True,
    replicaset='docker_dev_repl_set'
)
db = Collection(Database(client, 'flask'), 'notes')
notes = db.find({'note_id': 1650595246756}).limit(1)
# notes = client.flask.notes.find({'note_id': 27}).limit(1)
note_list = []
for note in notes:
    note.pop('_id')
    note_list.append(note)
print(note_list)
