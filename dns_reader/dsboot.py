import datetime
import json

from confluent_kafka import DeserializingConsumer, Producer
from confluent_kafka.cimpl import KafkaException
from confluent_kafka.serialization import StringDeserializer, StringSerializer
from odmantic import SyncEngine

from models.dns_query_models import RType
from models.state_models import Domain, QueryRequest, Query, AggregatedDomain
from services.dns_service import DNSService
from settings.settings import APPSettings
import uuid


class APPReader:

    PREFIX_DOMAIN = "dsboot"

    def __init__(self, engine: SyncEngine):
        self.app_settings = APPSettings()
        self.dns_service = DNSService()
        self.consumer = DeserializingConsumer(self._generate_consumer_config())
        self.producer = Producer(self._generate_producer_config())
        self.engine = engine

    def _generate_consumer_config(self):
        string_deserializer = StringDeserializer("utf_8")

        return {
            "bootstrap.servers": self.app_settings.brokers,
            "group.id": self.app_settings.group,
            "session.timeout.ms": 6000,
            "auto.offset.reset": "earliest",
            "key.deserializer": string_deserializer,
            "value.deserializer": string_deserializer,
        }

    def _generate_producer_config(self):
        string_serializer = StringSerializer("utf_8")

        return {
            "bootstrap.servers": self.app_settings.brokers,
        }

    def start(self):

        self.consumer.subscribe([self.app_settings.input_topic])
        print("Consuming from topic")
        while True:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                value = msg.value()

                domain = AggregatedDomain.parse_obj(json.loads(value))

                for parent in domain.parents_reference:
                    query_time = datetime.datetime.now()
                    query_cds, raw_query = self.dns_service.query_from_domain(
                        f"_dsboot.{domain.name}._signal.{parent.name}", RType.CDS, parent.name
                    )
                    query_cdnskey, raw_query = self.dns_service.query_from_domain(
                        f"_dsboot.{domain.name}._signal.{parent.name}", RType.CDNSKEY, parent.name
                    )
                    CDS_query = Query(
                                id=str(uuid.uuid4()),
                                query_time=query_time,
                                response=query_cds,
                            )
                    CDSNSKEY_query = Query(
                        id=str(uuid.uuid4()),
                        query_time=query_time,
                        response=query_cdnskey,
                    )

                    self.engine.save(CDSNSKEY_query)
                    self.engine.save(CDS_query)



    def query_next(self, domain):
        for parent in domain.parent_domains:
            if parent != domain.name:
                request = QueryRequest(domain=parent, parents=[], children=[domain.name])
                self.producer.produce(self.app_settings.input_topic, request.json())
