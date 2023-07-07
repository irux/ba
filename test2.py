from models.dns_query_models import RType
from services.dns_service import DNSService
import asyncio


from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

client = AsyncIOMotorClient("mongodb://root:example@localhost:27017/")
engine = AIOEngine(motor_client=client, database="dns")


async def test():
    service = DNSService()
    print(service.query_from_domain("elmerot.se", RType.NS))
    x,y = service.query_from_domain("elmerot.se", RType.NS)
    print(x,y)
    await engine.save(x)


asyncio.run(test())