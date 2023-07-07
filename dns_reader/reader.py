import datetime
import json

from confluent_kafka import DeserializingConsumer, Producer
from confluent_kafka.cimpl import KafkaException
from confluent_kafka.serialization import StringDeserializer, StringSerializer
from odmantic import SyncEngine

from models.dns_query_models import RType
from models.state_models import Domain, QueryRequest, Query
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

                request = QueryRequest.parse_obj(json.loads(value))

                print("Processing ", request.domain)

                domain = self.engine.find_one(Domain, Domain.name == request.domain)

                init_operation_time = datetime.datetime.now()

                if domain:
                    delta = domain.last_time_query - init_operation_time

                    domain.sub_domains = set(domain.sub_domains + request.children)
                    self.engine.save(domain)

                    if delta.days >= 2:
                        query, raw_query = self.dns_service.query_from_domain(
                            request.domain, RType.NS
                        )
                        domain.last_time_query = init_operation_time
                        if query.answer:
                            ns_domains = [
                                key for key, value in query.answer[0].items.items()
                            ]
                        else:
                            ns_domains = []
                        domain.parent_domains = ns_domains
                        domain.queries.append(
                            Query(
                                id=str(uuid.uuid4()),
                                query_time=init_operation_time,
                                response=query,
                            )
                        )
                        domain.ad_flag = query.AD_flag_set
                        self.engine.save(domain)
                else:
                    query, raw_query = self.dns_service.query_from_domain(
                        request.domain, RType.NS
                    )
                    domain = Domain(
                        name=request.domain,
                        ad_flag=query.AD_flag_set,
                        last_time_query=init_operation_time,
                        parent_domains=[
                            key for key, value in (query.answer[0].items.items() if len(query.answer) != 0 else [])
                        ]
                        + request.parents,
                        queries=[
                            Query(
                                id=str(uuid.uuid4()),
                                query_time=init_operation_time,
                                response=query,
                            )
                        ],
                        sub_domains=set(request.children),
                    )
                    self.engine.save(domain)

                self.query_next(domain)

    def query_next(self, domain):
        for parent in domain.parent_domains:
            if parent != domain.name:
                request = QueryRequest(domain=parent, parents=[], children=[domain.name])
                self.producer.produce(self.app_settings.input_topic, request.json())

