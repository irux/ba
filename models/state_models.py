from typing import Dict, List

from odmantic import Model, EmbeddedModel,Index, Field
from pydantic import BaseModel

from models.dns_query_models import DNSResponse
import datetime

class Query(EmbeddedModel):
    query_time: datetime.datetime
    response: DNSResponse
    id: str

class Domain(Model):
    queries: List[Query]
    ad_flag: bool
    name: str = Field(unique=True, Index=True)
    last_time_query: datetime.datetime
    sub_domains: List[str]
    parent_domains: List[str]

class QueryRequest(BaseModel):
    domain: str
    parents: List[str]
    children: List[str]


class SignalingRecord(Model):
    pass

class AggregatedDomain(Domain):
    parents_reference: List[Domain]

