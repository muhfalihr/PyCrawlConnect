import logging

from kafka import KafkaProducer
from helper.kafka_topic import TopicKafka
from json import dumps
from time import sleep


class ProduserKafka:
    def __init__(self, topic, bootstrap_servers, run):
        self.producer: KafkaProducer = KafkaProducer(
            bootstrap_servers=[bootstrap_servers],
            value_serializer=lambda x: dumps(x)
            .encode('utf-8')
        )
        self.run = run
        # Check whether the topic above already exists in the cluster or not,
        # if it doesn't then a new topic will be created according to the topic name above.
        self.tk: TopicKafka = TopicKafka(bootstrap_servers=bootstrap_servers)
        self.topic = self.tk.newtopic(
            topic=topic,
            num_partitions=1,
            replication_factor=1
        )
        self.logger = logging.getLogger(__name__)

    def produser(self, datas: dict):
        if self.run == "yes":
            datas = datas["result"]
            for data in datas:
                if data.get("title") == "":
                    continue
                else:
                    try:
                        resp = self.producer.send(
                            topic=self.topic,
                            value=data
                        )
                        self.logger.info(
                            f" [SUCCESS] Produced message to Kafka Topic [{self.topic}]")
                        sleep(5)
                    except Exception as e:
                        self.logger.error(
                            f" [ERROR] Produced message to Kafka Topic [{self.topic}]: {e}")
            self.producer.close()
        elif self.run == "no":
            return
