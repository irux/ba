#!/usr/bin/env python

import dns.resolver

ADDITIONAL_RDCLASS = 65535



name_server = '8.8.8.8'

domain = dns.name.from_text("cloudflare.com")
if not domain.is_absolute():
    domain = domain.concatenate(dns.name.root)

request = dns.message.make_query(domain, dns.rdatatype.SOA)
request.flags |= dns.flags.AD
request.find_rrset(request.additional, dns.name.root, ADDITIONAL_RDCLASS,
                   dns.rdatatype.OPT, create=True, force_unique=True)
response = dns.query.udp(request, name_server)
print(response)


"""
resolver = dns.resolver.Resolver(configure=False)

resolver.nameservers = ["8.8.8.8"]
resolver.set_flags(dns.flags.AD)
resolver.cache = False
answer = resolver.resolve("cloudflare.com", "NS", ADDITIONAL_RDCLASS)
print("The nameservers are:")
for rr in answer:
    print(rr.target)
    
"""