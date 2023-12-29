import os

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from kafka import KafkaConsumer
from datetime import datetime
from dotenv import load_dotenv
from json import loads


class ConsumerKafkaES:
    def __init__(self, topic, **configs):
        """"Consume records from a Kafka cluster.

        Arguments:
            *topics (str): optional list of topics to subscribe to. If not set,
                call :meth:`~kafka.KafkaConsumer.subscribe` or
                :meth:`~kafka.KafkaConsumer.assign` before consuming records.

        Keyword Arguments:
            bootstrap_servers: 'host[:port]' string (or list of 'host[:port]'
                strings) that the consumer should contact to bootstrap initial
                cluster metadata. This does not have to be the full node list.
                It just needs to have at least one broker that will respond to a
                Metadata API Request. Default port is 9092. If no servers are
                specified, will default to localhost:9092.
            client_id (str): A name for this client. This string is passed in
                each request to servers and can be used to identify specific
                server-side log entries that correspond to this client. Also
                submitted to GroupCoordinator for logging with respect to
                consumer group administration. Default: 'kafka-python-{version}'
            group_id (str or None): The name of the consumer group to join for dynamic
                partition assignment (if enabled), and to use for fetching and
                committing offsets. If None, auto-partition assignment (via
                group coordinator) and offset commits are disabled.
                Default: None
            key_deserializer (callable): Any callable that takes a
                raw message key and returns a deserialized key.
            value_deserializer (callable): Any callable that takes a
                raw message value and returns a deserialized value.
            fetch_min_bytes (int): Minimum amount of data the server should
                return for a fetch request, otherwise wait up to
                fetch_max_wait_ms for more data to accumulate. Default: 1.
            fetch_max_wait_ms (int): The maximum amount of time in milliseconds
                the server will block before answering the fetch request if
                there isn't sufficient data to immediately satisfy the
                requirement given by fetch_min_bytes. Default: 500.
            fetch_max_bytes (int): The maximum amount of data the server should
                return for a fetch request. This is not an absolute maximum, if the
                first message in the first non-empty partition of the fetch is
                larger than this value, the message will still be returned to
                ensure that the consumer can make progress. NOTE: consumer performs
                fetches to multiple brokers in parallel so memory usage will depend
                on the number of brokers containing partitions for the topic.
                Supported Kafka version >= 0.10.1.0. Default: 52428800 (50 MB).
            max_partition_fetch_bytes (int): The maximum amount of data
                per-partition the server will return. The maximum total memory
                used for a request = #partitions * max_partition_fetch_bytes.
                This size must be at least as large as the maximum message size
                the server allows or else it is possible for the producer to
                send messages larger than the consumer can fetch. If that
                happens, the consumer can get stuck trying to fetch a large
                message on a certain partition. Default: 1048576.
            request_timeout_ms (int): Client request timeout in milliseconds.
                Default: 305000.
            retry_backoff_ms (int): Milliseconds to backoff when retrying on
                errors. Default: 100.
            reconnect_backoff_ms (int): The amount of time in milliseconds to
                wait before attempting to reconnect to a given host.
                Default: 50.
            reconnect_backoff_max_ms (int): The maximum amount of time in
                milliseconds to backoff/wait when reconnecting to a broker that has
                repeatedly failed to connect. If provided, the backoff per host
                will increase exponentially for each consecutive connection
                failure, up to this maximum. Once the maximum is reached,
                reconnection attempts will continue periodically with this fixed
                rate. To avoid connection storms, a randomization factor of 0.2
                will be applied to the backoff resulting in a random range between
                20% below and 20% above the computed value. Default: 1000.
            max_in_flight_requests_per_connection (int): Requests are pipelined
                to kafka brokers up to this number of maximum requests per
                broker connection. Default: 5.
            auto_offset_reset (str): A policy for resetting offsets on
                OffsetOutOfRange errors: 'earliest' will move to the oldest
                available message, 'latest' will move to the most recent. Any
                other value will raise the exception. Default: 'latest'.
            enable_auto_commit (bool): If True , the consumer's offset will be
                periodically committed in the background. Default: True.
            auto_commit_interval_ms (int): Number of milliseconds between automatic
                offset commits, if enable_auto_commit is True. Default: 5000.
            default_offset_commit_callback (callable): Called as
                callback(offsets, response) response will be either an Exception
                or an OffsetCommitResponse struct. This callback can be used to
                trigger custom actions when a commit request completes.
            check_crcs (bool): Automatically check the CRC32 of the records
                consumed. This ensures no on-the-wire or on-disk corruption to
                the messages occurred. This check adds some overhead, so it may
                be disabled in cases seeking extreme performance. Default: True
            metadata_max_age_ms (int): The period of time in milliseconds after
                which we force a refresh of metadata, even if we haven't seen any
                partition leadership changes to proactively discover any new
                brokers or partitions. Default: 300000
            partition_assignment_strategy (list): List of objects to use to
                distribute partition ownership amongst consumer instances when
                group management is used.
                Default: [RangePartitionAssignor, RoundRobinPartitionAssignor]
            max_poll_records (int): The maximum number of records returned in a
                single call to :meth:`~kafka.KafkaConsumer.poll`. Default: 500
            max_poll_interval_ms (int): The maximum delay between invocations of
                :meth:`~kafka.KafkaConsumer.poll` when using consumer group
                management. This places an upper bound on the amount of time that
                the consumer can be idle before fetching more records. If
                :meth:`~kafka.KafkaConsumer.poll` is not called before expiration
                of this timeout, then the consumer is considered failed and the
                group will rebalance in order to reassign the partitions to another
                member. Default 300000
            session_timeout_ms (int): The timeout used to detect failures when
                using Kafka's group management facilities. The consumer sends
                periodic heartbeats to indicate its liveness to the broker. If
                no heartbeats are received by the broker before the expiration of
                this session timeout, then the broker will remove this consumer
                from the group and initiate a rebalance. Note that the value must
                be in the allowable range as configured in the broker configuration
                by group.min.session.timeout.ms and group.max.session.timeout.ms.
                Default: 10000
            heartbeat_interval_ms (int): The expected time in milliseconds
                between heartbeats to the consumer coordinator when using
                Kafka's group management facilities. Heartbeats are used to ensure
                that the consumer's session stays active and to facilitate
                rebalancing when new consumers join or leave the group. The
                value must be set lower than session_timeout_ms, but typically
                should be set no higher than 1/3 of that value. It can be
                adjusted even lower to control the expected time for normal
                rebalances. Default: 3000
            receive_buffer_bytes (int): The size of the TCP receive buffer
                (SO_RCVBUF) to use when reading data. Default: None (relies on
                system defaults). The java client defaults to 32768.
            send_buffer_bytes (int): The size of the TCP send buffer
                (SO_SNDBUF) to use when sending data. Default: None (relies on
                system defaults). The java client defaults to 131072.
            socket_options (list): List of tuple-arguments to socket.setsockopt
                to apply to broker connection sockets. Default:
                [(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)]
            consumer_timeout_ms (int): number of milliseconds to block during
                message iteration before raising StopIteration (i.e., ending the
                iterator). Default block forever [float('inf')].
            security_protocol (str): Protocol used to communicate with brokers.
                Valid values are: PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL.
                Default: PLAINTEXT.
            ssl_context (ssl.SSLContext): Pre-configured SSLContext for wrapping
                socket connections. If provided, all other ssl_* configurations
                will be ignored. Default: None.
            ssl_check_hostname (bool): Flag to configure whether ssl handshake
                should verify that the certificate matches the brokers hostname.
                Default: True.
            ssl_cafile (str): Optional filename of ca file to use in certificate
                verification. Default: None.
            ssl_certfile (str): Optional filename of file in pem format containing
                the client certificate, as well as any ca certificates needed to
                establish the certificate's authenticity. Default: None.
            ssl_keyfile (str): Optional filename containing the client private key.
                Default: None.
            ssl_password (str): Optional password to be used when loading the
                certificate chain. Default: None.
            ssl_crlfile (str): Optional filename containing the CRL to check for
                certificate expiration. By default, no CRL check is done. When
                providing a file, only the leaf certificate will be checked against
                this CRL. The CRL can only be checked with Python 3.4+ or 2.7.9+.
                Default: None.
            ssl_ciphers (str): optionally set the available ciphers for ssl
                connections. It should be a string in the OpenSSL cipher list
                format. If no cipher can be selected (because compile-time options
                or other configuration forbids use of all the specified ciphers),
                an ssl.SSLError will be raised. See ssl.SSLContext.set_ciphers
            api_version (tuple): Specify which Kafka API version to use. If set to
                None, the client will attempt to infer the broker version by probing
                various APIs. Different versions enable different functionality.

                Examples:
                    (0, 9) enables full group coordination features with automatic
                        partition assignment and rebalancing,
                    (0, 8, 2) enables kafka-storage offset commits with manual
                        partition assignment only,
                    (0, 8, 1) enables zookeeper-storage offset commits with manual
                        partition assignment only,
                    (0, 8, 0) enables basic functionality but requires manual
                        partition assignment and offset management.

                Default: None
            api_version_auto_timeout_ms (int): number of milliseconds to throw a
                timeout exception from the constructor when checking the broker
                api version. Only applies if api_version set to None.
            connections_max_idle_ms: Close idle connections after the number of
                milliseconds specified by this config. The broker closes idle
                connections after connections.max.idle.ms, so this avoids hitting
                unexpected socket disconnected errors on the client.
                Default: 540000
            metric_reporters (list): A list of classes to use as metrics reporters.
                Implementing the AbstractMetricsReporter interface allows plugging
                in classes that will be notified of new metric creation. Default: []
            metrics_num_samples (int): The number of samples maintained to compute
                metrics. Default: 2
            metrics_sample_window_ms (int): The maximum age in milliseconds of
                samples used to compute metrics. Default: 30000
            selector (selectors.BaseSelector): Provide a specific selector
                implementation to use for I/O multiplexing.
                Default: selectors.DefaultSelector
            exclude_internal_topics (bool): Whether records from internal topics
                (such as offsets) should be exposed to the consumer. If set to True
                the only way to receive records from an internal topic is
                subscribing to it. Requires 0.10+ Default: True
            sasl_mechanism (str): Authentication mechanism when security_protocol
                is configured for SASL_PLAINTEXT or SASL_SSL. Valid values are:
                PLAIN, GSSAPI, OAUTHBEARER, SCRAM-SHA-256, SCRAM-SHA-512.
            sasl_plain_username (str): username for sasl PLAIN and SCRAM authentication.
                Required if sasl_mechanism is PLAIN or one of the SCRAM mechanisms.
            sasl_plain_password (str): password for sasl PLAIN and SCRAM authentication.
                Required if sasl_mechanism is PLAIN or one of the SCRAM mechanisms.
            sasl_kerberos_service_name (str): Service name to include in GSSAPI
                sasl mechanism handshake. Default: 'kafka'
            sasl_kerberos_domain_name (str): kerberos domain name to use in GSSAPI
                sasl mechanism handshake. Default: one of bootstrap servers
            sasl_oauth_token_provider (AbstractTokenProvider): OAuthBearer token provider
                instance. (See kafka.oauth.abstract). Default: None
        """
        if topic is not None:
            if not isinstance(topic, str):
                raise TypeError(
                    "Invalid \"ConsumerKafkaES\" parameter, value must be type str, {} passed".format(
                        type(topic).__name__)
                )
            if isinstance(topic, str):
                topic = str(topic)
        else:
            raise ValueError(
                f"Sorry, the `topic` parameter is required. Please enter your topic."
            )
        self.consumer: KafkaConsumer = KafkaConsumer(
            topic,
            value_deserializer=lambda x: loads(x.decode('utf-8')),
            **configs,
        )
        self.configs = configs
        self.topic = topic

    def elastic(self, hosts: str | list, **kwargs):
        """
        :arg hosts: list of nodes, or a single node, we should connect to.
            Node should be a dictionary ({"host": "localhost", "port": 9200}),
            the entire dictionary will be passed to the :class:`~elasticsearch.Connection`
            class as kwargs, or a string in the format of ``host[:port]`` which will be
            translated to a dictionary automatically.  If no value is given the
            :class:`~elasticsearch.Connection` class defaults will be used.

        :arg transport_class: :class:`~elasticsearch.Transport` subclass to use.

        :arg kwargs: any additional arguments will be passed on to the
            :class:`~elasticsearch.Transport` class and, subsequently, to the
            :class:`~elasticsearch.Connection` instances.
        """
        if hosts is not None:
            if not isinstance(hosts, (str, list)):
                raise TypeError(
                    "Invalid \"elastic\" parameter, value must be type str|list, {} passed".format(
                        type(hosts).__name__)
                )
            if isinstance(hosts, (str, list)):
                hosts = hosts
        else:
            raise ValueError(
                f"Sorry, the `hosts` parameter is required. Please enter hosts value parameter."
            )
        client: Elasticsearch = Elasticsearch(
            hosts=hosts,
            **kwargs
        )
        index_name = f'data-{self.configs["group_id"]}'
        for msg in self.consumer:
            resp = client.index(
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
        """
        Prints Consumer Data results to your Console.
        """
        for msg in self.consumer:
            print(msg.value)


def main():
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

    consumen: ConsumerKafkaES = ConsumerKafkaES(
        topic=topic,
        group_id=groupid,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset=auto_offset_reset,
        enable_auto_commit=True
    )

    # The book topic is not indexed in ElasticSearch because the field structure is different.
    if forward == "yes" or topic != "book":
        consumen.elastic(
            hosts=host,
            http_auth=(username, password),
            verify_certs=True,
            timeout=60
        )
    else:
        consumen.consumer_msg()


if __name__ == "__main__":
    main()
