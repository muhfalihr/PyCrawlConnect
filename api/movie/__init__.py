from helper.kafka_produser import ProduserKafka
from dotenv import load_dotenv

import os


load_dotenv()

run = os.environ.get("RUNKAFKA")
bootstrap_servers = os.environ.get("IPKAFKA")
script_path = os.path.realpath(__file__)
topic = os.path.dirname(script_path).split("/")[-1]

pk = ProduserKafka(topic=topic, bootstrap_servers=bootstrap_servers, run=run)
