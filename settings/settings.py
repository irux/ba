from pydantic import BaseSettings, Field


class APPSettings(BaseSettings):
    brokers: str = Field(..., env="BROKERS")
    group: str = Field(..., env="CONSUMER_GROUP")
    input_topic: str = Field(..., env="INPUT_TOPIC")
