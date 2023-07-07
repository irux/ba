from enum import IntEnum, IntFlag
from typing import Optional, Any, Dict, List

from odmantic import Model, EmbeddedModel


class RType(IntEnum):
    TYPE0 = 0
    NONE = 0
    A = 1
    NS = 2
    MD = 3
    MF = 4
    CNAME = 5
    SOA = 6
    MB = 7
    MG = 8
    MR = 9
    NULL = 10
    WKS = 11
    PTR = 12
    HINFO = 13
    MINFO = 14
    MX = 15
    TXT = 16
    RP = 17
    AFSDB = 18
    X25 = 19
    ISDN = 20
    RT = 21
    NSAP = 22
    NSAP_PTR = 23
    SIG = 24
    KEY = 25
    PX = 26
    GPOS = 27
    AAAA = 28
    LOC = 29
    NXT = 30
    SRV = 33
    NAPTR = 35
    KX = 36
    CERT = 37
    A6 = 38
    DNAME = 39
    OPT = 41
    APL = 42
    DS = 43
    SSHFP = 44
    IPSECKEY = 45
    RRSIG = 46
    NSEC = 47
    DNSKEY = 48
    DHCID = 49
    NSEC3 = 50
    NSEC3PARAM = 51
    TLSA = 52
    SMIMEA = 53
    HIP = 55
    NINFO = 56
    CDS = 59
    CDNSKEY = 60
    OPENPGPKEY = 61
    CSYNC = 62
    ZONEMD = 63
    SVCB = 64
    HTTPS = 65
    SPF = 99
    UNSPEC = 103
    NID = 104
    L32 = 105
    L64 = 106
    LP = 107
    EUI48 = 108
    EUI64 = 109
    TKEY = 249
    TSIG = 250
    IXFR = 251
    AXFR = 252
    MAILB = 253
    MAILA = 254
    ANY = 255
    URI = 256
    CAA = 257
    AVC = 258
    AMTRELAY = 260
    TA = 32768
    DLV = 32769


class RClass(IntEnum):
    RESERVED0 = 0
    IN = 1
    INTERNET = IN
    CH = 3
    CHAOS = CH
    HS = 4
    HESIOD = HS
    NONE = 254
    ANY = 255


class Flag(IntFlag):
    #: Query Response
    QR = 0x8000
    #: Authoritative Answer
    AA = 0x0400
    #: Truncated Response
    TC = 0x0200
    #: Recursion Desired
    RD = 0x0100
    #: Recursion Available
    RA = 0x0080
    #: Authentic Data
    AD = 0x0020
    #: Checking Disabled
    CD = 0x0010


class RRSet(EmbeddedModel):
    rdclass: RClass
    rdtype: RType
    items: Dict[Any, Any] = {}
    ttl: int
    name: str


class DNSResponse(EmbeddedModel):
    response_id: int
    edns: int
    edns_flags: int
    origin: Optional[str]
    payload: int
    time: float
    tsig: Optional[str]
    tsig_ctx: Optional[str]
    tsig_error: Optional[str]
    answer: List[RRSet] = []
    authority: List[RRSet] = []
    question: List[RRSet] = []
    errors: List[RRSet] = []
    additional: List[RRSet] = []
    flags: Flag
    AD_flag_set: bool
    raw_response: str
