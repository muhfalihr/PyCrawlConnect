from kafka import KafkaAdminClient
from kafka.admin import NewTopic


class TopicKafka:
    def __init__(self, bootstrap_servers):
        self.adminclient: KafkaAdminClient = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers
        )

    def newtopic(self,  topic: str, num_partitions: int = 1, replication_factor: int = 1):
        topic_metadata = self.adminclient.list_topics()
        # Check whether the topic from the input is available in the cluster or not.
        if topic in topic_metadata:
            return topic
        else:
            new_topic: NewTopic = NewTopic(
                name=topic,
                num_partitions=num_partitions,
                replication_factor=replication_factor
            )
            craetetopic = self.adminclient.create_topics(
                new_topics=[new_topic],
                timeout_ms=5000
            )
            return topic
