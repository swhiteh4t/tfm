from io import StringIO
from pymongo import MongoClient
import json
from DarkNetScraper.output.colors import ColoredText
from DarkNetScraper.io.file_handlers import save_json
from .time.getime import get_formatted_time
from .config import MONGO_URI, MONGO_DB_NAME
import pandas as pd


class DBConnector:
    client = None
    collection = None

    def __init__(self) -> None:
       self.entries = []
       # Connection string is read from the MONGO_URI environment variable
       self.client = MongoClient(MONGO_URI)
       DB_NAME = MONGO_DB_NAME

       #Get database names
       databases = self.client.list_database_names()
       # Check if the database exists
       if DB_NAME not in databases:
            # Create the database
            self.db = self.client[DB_NAME]
            print(f"Database '{DB_NAME}' created.")
       else:
            # Database already exists
            self.db = self.client[DB_NAME]
            print(f"Database '{DB_NAME}' already exists.")

       self.collection_name = "Search-" + get_formatted_time()
       self.collection = self.db[self.collection_name]

    def add_entry_generate(self,title,content,category,verbose=False):
        if verbose:
            print(ColoredText("Added entry to collection " + self.collection_name,'white'))
        entry = {
            'title' : title,
            'content' : content,
            'category' : category,
        }
        self.entries.append(entry)



    def add_entry(self,title="",link="",content="",category="",summary="", emails="", address="", phone="", ipv4="", ipv6="", cloud="",verbose=False):
        entry = {
            "Title" : title,
            "Link" : link,
            "Category" : category,
            "Content" : content,
            "Summary" : summary,
            "Email" : emails,
            "Address" : address,
            "Phone" : phone,
            "IPv4" : ipv4,
            "IPv6" : ipv6,
            "CloudDomains" : cloud,
        }
        if verbose:
            print(ColoredText("Added entry to collection " + self.collection_name,'white'))
        self.entries.append(entry)

    def save_db(self):
        if len(self.entries):
            self.collection.insert_many(self.entries)

    def save_to_file(self):
        save_json(self.collection_name + ".json", self.entries)
        df = pd.read_json(StringIO(json.dumps(self.entries)))
        df.to_csv(self.collection_name + ".csv", index=False)
