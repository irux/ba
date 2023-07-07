from odmantic import SyncEngine
from pymongo import MongoClient

from dns_reader.reader import APPReader

client = MongoClient("mongodb://root:example@localhost:27017/")
engine = SyncEngine(client=client, database="dns")


reader = APPReader(engine)
reader.start()
