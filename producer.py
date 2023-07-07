import datetime
import json
import sys
from confluent_kafka import DeserializingConsumer, Producer
from confluent_kafka.cimpl import KafkaException
from confluent_kafka.serialization import StringDeserializer, StringSerializer
from odmantic import SyncEngine

from models.dns_query_models import RType
from models.state_models import Domain, QueryRequest, Query
from services.dns_service import DNSService
from settings.settings import APPSettings
import uuid
import time
app_settings = APPSettings()
producer = Producer({
            "bootstrap.servers": app_settings.brokers,
        })

with open("top-1m.csv", "r") as f:
    for line in f:
        domain = line.split(",")[1].strip()
        query = QueryRequest(domain=domain, parents=[], children=[])
        print("Sending ", domain)
        producer.produce(app_settings.input_topic, query.json())
        time.sleep(2)
