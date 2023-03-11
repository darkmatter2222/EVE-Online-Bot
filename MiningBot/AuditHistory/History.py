import sys, os, decimal, json, time
import pyautogui
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import socket
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

env_path = Path(fr"{os.environ['USERPROFILE']}\.env")
load_dotenv(dotenv_path=env_path)

log_template = {
    'datetime': datetime.utcnow(),
    'action': None,
    'context': None

}

class History:
    # make singleton
    def __new__(cls, config_dir=r'..\Configs\configs.json'):
        if not hasattr(cls, 'instance'):
            cls.instance = super(History, cls).__new__(cls)
        return cls.instance

    def __init__(self, config_dir=r'..\Configs\configs.json'):
        self.config_dir = config_dir
        self.config = json.load(open(self.config_dir))[socket.gethostname()]

        self.client = MongoClient(self.config['mongo_host'],
                                  username=os.getenv("eve_username"),
                                  password=os.getenv("eve_password"))
        self.db = self.client[self.config['db_name']]
        self.collection = self.db[self.config['collection_name']]
        self.temp = 0

    def insert_payload(self, payload):
        insert_id = None
        try:
            insert_id = self.collection.insert_one(payload).inserted_id
        except Exception as e:
            logger.info(e)
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

    def log_unload(self, cargo_volume):
        log = log_template.copy()
        log['datetime'] = datetime.utcnow()
        log['action'] = 'Unload'
        log['context'] = cargo_volume

        self.insert_payload(log)

    def log_extraction(self, action='Both_Miners'):
        log = log_template.copy()
        log['datetime'] = datetime.utcnow()
        log['action'] = 'Extraction'
        log['context'] = action

        self.insert_payload(log)

    def log_stale_mining(self, fault='unknown'):
        log = log_template.copy()
        log['datetime'] = datetime.utcnow()
        log['action'] = 'Stale Mining Reset'
        log['context'] = fault

        self.insert_payload(log)

    def log_field_depleted(self):
        log = log_template.copy()
        log['datetime'] = datetime.utcnow()
        log['action'] = 'Field_depleted'
        log['context'] = ''

        self.insert_payload(log)

    def log_fault(self, fault):
        log = log_template.copy()
        log['datetime'] = datetime.utcnow()
        log['action'] = 'Fault'
        log['context'] = fault

        self.insert_payload(log)

    def log_image_class_low_confidence_fault_result(self, result):
        log = log_template.copy()
        log['datetime'] = datetime.utcnow()
        log['action'] = 'image_class_low_confidence_fault'
        log['context'] = result

        self.insert_payload(log)

    def log_main_loop_activity(self, action, result):
        log = log_template.copy()
        log['datetime'] = datetime.utcnow()
        log['action'] = f'Main_Loop_{action}'
        log['context'] = result

        self.insert_payload(log)
