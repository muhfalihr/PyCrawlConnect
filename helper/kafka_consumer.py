import logging
import os

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from kafka import KafkaConsumer
from datetime import datetime
from dotenv import load_dotenv
from json import loads


class ConsumerKafka:
    def __init__(self, topic: str, group_id: str, bootstrap_servers: str, auto_offset_reset: str):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[bootstrap_servers],
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=True,
            group_id=group_id,
            value_deserializer=lambda x: loads(x.decode('utf-8'))
        )
        self.topic = topic
        self.logger = logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s",
            level=logging.INFO
        )

    def elastic(self, host, username, password):
        es = Elasticsearch(
            hosts=host,
            http_auth=(username, password),
            verify_certs=True,
            timeout=60
        )
        date = datetime.now().strftime("%Y%m%d")
        index_name = f'crawl-data-{date}'
        for msg in self.consumer:
            resp = es.index(
                index=index_name,
                document=msg.value,
                id=msg.value["id"],
                refresh=True,
                pretty=True
            )
            print(
                f"{datetime.now()} - [INFO] - Index data to {index_name} with document id : {resp['_id']}")
        self.consumer.close()

    def consumer_msg(self):
        for msg in self.consumer:
            print(msg.value)


if __name__ == "__main__":
    load_dotenv()

    # kafka
    bootstrap_servers = os.environ.get("IPKAFKA")
    topic = os.environ.get("TOPIC_FOR_CONSUME")
    auto_offset_reset = os.environ.get("AUTO_OFFSET_RESET")
    forward = os.environ.get("FORWARD_TO_ELASTIC")
    groupid = os.environ.get("GROUPID")

    # elastic
    host = os.environ.get("HOST")
    username = os.environ.get("USERNAME")
    password = os.environ.get("PASSWORD")

    consumen = ConsumerKafka(
        topic=topic,
        group_id=groupid,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset=auto_offset_reset
    )

    if forward == "yes":
        consumen.elastic(
            host=host,
            username=username,
            password=password
        )
    else:
        consumen.consumer_msg()
