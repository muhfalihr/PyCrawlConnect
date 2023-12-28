from kafka import KafkaAdminClient
from kafka.admin import NewTopic


class TopicKafka:
    def __init__(self, **configs):
        self.adminclient: KafkaAdminClient = KafkaAdminClient(
            **configs
        )

    def newtopic(
            self,
            name: str,
            num_partitions: int,
            replication_factor: int,
            replica_assignments=None,
            topic_configs=None,
            timeout_ms=None,
            validate_only=False
    ):
        """Create new topics in the cluster.

        :param new_topics: A list of NewTopic objects.
        :param timeout_ms: Milliseconds to wait for new topics to be created
            before the broker returns.
        :param validate_only: If True, don't actually create new topics.
            Not supported by all versions. Default: False
        :return: Appropriate version of CreateTopicResponse class.
        """
        topic_metadata = self.adminclient.list_topics()
        # Check whether the topic from the input is available in the cluster or not.
        if name not in topic_metadata:
            new_topic: NewTopic = NewTopic(
                name,
                num_partitions,
                replication_factor,
                replica_assignments,
                topic_configs
            )
            create_topic = self.adminclient.create_topics(
                [new_topic],
                timeout_ms,
                validate_only
            )
        return name
