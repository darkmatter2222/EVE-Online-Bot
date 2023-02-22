import sys, os, decimal, json, time
import pyautogui
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import socket
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(fr"{os.environ['USERPROFILE']}\.env")
load_dotenv(dotenv_path=env_path)

log_template = {
    'datetime': datetime.utcnow(),
    'action': None,
    'context': None

}

class History:
    def __init__(self, config_dir=r'..\Configs\configs.json'):
        self.config_dir = config_dir
        self.config = json.load(open(self.config_dir))[socket.gethostname()]

        self.client = MongoClient(self.config['mongo_host'],
                                  username=os.getenv("eve_username"),
                                  password=os.getenv("eve_password"))
        self.db = self.client[self.config['db_name']]
        self.collection = self.db[self.config['collection_name']]

    def insert_payload(self, payload):
        insert_id = None
        try:
            insert_id = self.collection.insert_one(payload).inserted_id
        except Exception as e:
            print(e)
            pass

    def empty_collection(self):
        self.collection.delete_many({})

    def get_all(self):
        results = []
        doc_cur = self.collection.find({})
        for doc in doc_cur:
            results.append(doc)
        return results

    def log_navigate(self, destination):
        log = log_template.copy()
        log['datetime'] = datetime.utcnow()
        log['action'] = 'Navigating'
        log['context'] = destination

        self.insert_payload(log)

    def log_unload(self):
        log = log_template.copy()
        log['datetime'] = datetime.utcnow()
        log['action'] = 'Unload'
        log['context'] = ''

        self.insert_payload(log)

    def log_extraction(self):
        log = log_template.copy()
        log['datetime'] = datetime.utcnow()
        log['action'] = 'Extraction'
        log['context'] = ''

        self.insert_payload(log)

    def log_stale_mining(self):
        log = log_template.copy()
        log['datetime'] = datetime.utcnow()
        log['action'] = 'Stale Mining Reset'
        log['context'] = ''

        self.insert_payload(log)

