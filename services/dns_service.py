import random
from typing import List, Dict, Union, Tuple

import dns.message
import dns.message
import dns.name
import dns.query
import dns.rdataclass
import dns.rdatatype
import dns.resolver
from dns.message import Message
from dns.name import Name
from dns.rrset import RRset

from models.dns_query_models import DNSResponse, RType, Flag


class DNSService:

    _ADDITIONAL_RDCLASS = 65535

    def __init__(self, custom_nameservers=None):
        if custom_nameservers is None:
            custom_nameservers = []

        self._nameservers = self._get_name_servers_with_default(custom_nameservers)

    def query_from_domain(
        self, domain: str, query_type: RType, custom_nameserver=None
    ) -> Tuple[DNSResponse, str]:
        domain = dns.name.from_text(domain)
        if not domain.is_absolute():
            domain = domain.concatenate(dns.name.root)

        request = self._get_query_from(domain, query_type)
        name_server = custom_nameserver or random.choice(self._nameservers)
        response = dns.query.udp(request, name_server)
        query_parsed = self._parse_dns_query(response)
        return query_parsed, str(response)

    def _get_query_from(self, domain: Name, query_type: RType):
        request = dns.message.make_query(domain, query_type)
        request.flags |= dns.flags.AD
        request.find_rrset(
            request.additional,
            dns.name.root,
            self._ADDITIONAL_RDCLASS,
            dns.rdatatype.OPT,
            create=True,
            force_unique=True,
        )
        return request

    def _get_name_servers_with_default(
        self, custom_nameservers: List[str]
    ) -> List[str]:
        return list(set(["8.8.8.8", "1.1.1.1"] + custom_nameservers))

    def _parse_dns_query(self, response: Message) -> DNSResponse:
        flags = Flag(response.flags)
        return DNSResponse(
            response_id=response.id,
            edns=response.edns,
            edns_flags=response.ednsflags,
            flags=flags,
            payload=response.payload,
            additional=self._transform_rrset_to_dict(response.sections[3]),
            answer=self._transform_rrset_to_dict(response.sections[1]),
            authority=self._transform_rrset_to_dict(response.sections[2]),
            origin=response.origin,
            question=self._transform_rrset_to_dict(response.sections[0]),
            time=response.time,
            tsig=response.tsig,
            tsig_error=response.tsig_error,
            AD_flag_set=(Flag.AD in flags),
            raw_response=str(response)
        )

    def _transform_rrset_to_dict(
        self, rrsets: List[RRset]
    ) -> List[Dict[str, Union[Dict, int, str]]]:
        return [
            {
                "items": {str(key): value for key, value in rrset.items.items()},
                "rdclass": rrset.rdclass,
                "rdtype": rrset.rdtype,
                "ttl": rrset.ttl,
                "name": str(rrset.name),
            }
            for rrset in rrsets
        ]

