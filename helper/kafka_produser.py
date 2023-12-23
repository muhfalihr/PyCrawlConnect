from kafka import KafkaProducer
from json import dumps
from time import sleep


class ProduserKafka:
    def __init__(self, topic):
        self.kp = KafkaProducer(
            bootstrap_servers=['192.168.57.9:9092'],
            value_serializer=lambda x: dumps(x)
            .encode('utf-8')
        )
        self.topic = topic

    def produser(self, datas: dict):
        datas = datas["data"]["result"]
        for data in datas:
            if (data.get("title") == "") or (data.get("content") == ""):
                continue
            else:
                print(data)
                self.kp.send(
                    topic=self.topic,
                    value=data
                )
                sleep(5)
