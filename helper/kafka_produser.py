import logging

from kafka import KafkaProducer
from helper.kafka_topic import TopicKafka
from json import dumps
from time import sleep


class ProduserKafka:
    def __init__(self, topic, run, **configs):
        """A Kafka client that publishes records to the Kafka cluster.

        Keyword Arguments:
            bootstrap_servers: 'host[:port]' string (or list of 'host[:port]'
                strings) that the producer should contact to bootstrap initial
                cluster metadata. This does not have to be the full node list.
                It just needs to have at least one broker that will respond to a
                Metadata API Request. Default port is 9092. If no servers are
                specified, will default to localhost:9092.
            client_id (str): a name for this client. This string is passed in
                each request to servers and can be used to identify specific
                server-side log entries that correspond to this client.
                Default: 'kafka-python-producer-#' (appended with a unique number
                per instance)
            key_serializer (callable): used to convert user-supplied keys to bytes
                If not None, called as f(key), should return bytes. Default: None.
            value_serializer (callable): used to convert user-supplied message
                values to bytes. If not None, called as f(value), should return
                bytes. Default: None.
            acks (0, 1, 'all'): The number of acknowledgments the producer requires
                the leader to have received before considering a request complete.
                This controls the durability of records that are sent. The
                following settings are common:

                0: Producer will not wait for any acknowledgment from the server.
                    The message will immediately be added to the socket
                    buffer and considered sent. No guarantee can be made that the
                    server has received the record in this case, and the retries
                    configuration will not take effect (as the client won't
                    generally know of any failures). The offset given back for each
                    record will always be set to -1.
                1: Wait for leader to write the record to its local log only.
                    Broker will respond without awaiting full acknowledgement from
                    all followers. In this case should the leader fail immediately
                    after acknowledging the record but before the followers have
                    replicated it then the record will be lost.
                all: Wait for the full set of in-sync replicas to write the record.
                    This guarantees that the record will not be lost as long as at
                    least one in-sync replica remains alive. This is the strongest
                    available guarantee.
                If unset, defaults to acks=1.
            compression_type (str): The compression type for all data generated by
                the producer. Valid values are 'gzip', 'snappy', 'lz4', 'zstd' or None.
                Compression is of full batches of data, so the efficacy of batching
                will also impact the compression ratio (more batching means better
                compression). Default: None.
            retries (int): Setting a value greater than zero will cause the client
                to resend any record whose send fails with a potentially transient
                error. Note that this retry is no different than if the client
                resent the record upon receiving the error. Allowing retries
                without setting max_in_flight_requests_per_connection to 1 will
                potentially change the ordering of records because if two batches
                are sent to a single partition, and the first fails and is retried
                but the second succeeds, then the records in the second batch may
                appear first.
                Default: 0.
            batch_size (int): Requests sent to brokers will contain multiple
                batches, one for each partition with data available to be sent.
                A small batch size will make batching less common and may reduce
                throughput (a batch size of zero will disable batching entirely).
                Default: 16384
            linger_ms (int): The producer groups together any records that arrive
                in between request transmissions into a single batched request.
                Normally this occurs only under load when records arrive faster
                than they can be sent out. However in some circumstances the client
                may want to reduce the number of requests even under moderate load.
                This setting accomplishes this by adding a small amount of
                artificial delay; that is, rather than immediately sending out a
                record the producer will wait for up to the given delay to allow
                other records to be sent so that the sends can be batched together.
                This can be thought of as analogous to Nagle's algorithm in TCP.
                This setting gives the upper bound on the delay for batching: once
                we get batch_size worth of records for a partition it will be sent
                immediately regardless of this setting, however if we have fewer
                than this many bytes accumulated for this partition we will
                'linger' for the specified time waiting for more records to show
                up. This setting defaults to 0 (i.e. no delay). Setting linger_ms=5
                would have the effect of reducing the number of requests sent but
                would add up to 5ms of latency to records sent in the absence of
                load. Default: 0.
            partitioner (callable): Callable used to determine which partition
                each message is assigned to. Called (after key serialization):
                partitioner(key_bytes, all_partitions, available_partitions).
                The default partitioner implementation hashes each non-None key
                using the same murmur2 algorithm as the java client so that
                messages with the same key are assigned to the same partition.
                When a key is None, the message is delivered to a random partition
                (filtered to partitions with available leaders only, if possible).
            buffer_memory (int): The total bytes of memory the producer should use
                to buffer records waiting to be sent to the server. If records are
                sent faster than they can be delivered to the server the producer
                will block up to max_block_ms, raising an exception on timeout.
                In the current implementation, this setting is an approximation.
                Default: 33554432 (32MB)
            connections_max_idle_ms: Close idle connections after the number of
                milliseconds specified by this config. The broker closes idle
                connections after connections.max.idle.ms, so this avoids hitting
                unexpected socket disconnected errors on the client.
                Default: 540000
            max_block_ms (int): Number of milliseconds to block during
                :meth:`~kafka.KafkaProducer.send` and
                :meth:`~kafka.KafkaProducer.partitions_for`. These methods can be
                blocked either because the buffer is full or metadata unavailable.
                Blocking in the user-supplied serializers or partitioner will not be
                counted against this timeout. Default: 60000.
            max_request_size (int): The maximum size of a request. This is also
                effectively a cap on the maximum record size. Note that the server
                has its own cap on record size which may be different from this.
                This setting will limit the number of record batches the producer
                will send in a single request to avoid sending huge requests.
                Default: 1048576.
            metadata_max_age_ms (int): The period of time in milliseconds after
                which we force a refresh of metadata even if we haven't seen any
                partition leadership changes to proactively discover any new
                brokers or partitions. Default: 300000
            retry_backoff_ms (int): Milliseconds to backoff when retrying on
                errors. Default: 100.
            request_timeout_ms (int): Client request timeout in milliseconds.
                Default: 30000.
            receive_buffer_bytes (int): The size of the TCP receive buffer
                (SO_RCVBUF) to use when reading data. Default: None (relies on
                system defaults). Java client defaults to 32768.
            send_buffer_bytes (int): The size of the TCP send buffer
                (SO_SNDBUF) to use when sending data. Default: None (relies on
                system defaults). Java client defaults to 131072.
            socket_options (list): List of tuple-arguments to socket.setsockopt
                to apply to broker connection sockets. Default:
                [(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)]
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
                broker connection. Note that if this setting is set to be greater
                than 1 and there are failed sends, there is a risk of message
                re-ordering due to retries (i.e., if retries are enabled).
                Default: 5.
            security_protocol (str): Protocol used to communicate with brokers.
                Valid values are: PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL.
                Default: PLAINTEXT.
            ssl_context (ssl.SSLContext): pre-configured SSLContext for wrapping
                socket connections. If provided, all other ssl_* configurations
                will be ignored. Default: None.
            ssl_check_hostname (bool): flag to configure whether ssl handshake
                should verify that the certificate matches the brokers hostname.
                default: true.
            ssl_cafile (str): optional filename of ca file to use in certificate
                veriication. default: none.
            ssl_certfile (str): optional filename of file in pem format containing
                the client certificate, as well as any ca certificates needed to
                establish the certificate's authenticity. default: none.
            ssl_keyfile (str): optional filename containing the client private key.
                default: none.
            ssl_password (str): optional password to be used when loading the
                certificate chain. default: none.
            ssl_crlfile (str): optional filename containing the CRL to check for
                certificate expiration. By default, no CRL check is done. When
                providing a file, only the leaf certificate will be checked against
                this CRL. The CRL can only be checked with Python 3.4+ or 2.7.9+.
                default: none.
            ssl_ciphers (str): optionally set the available ciphers for ssl
                connections. It should be a string in the OpenSSL cipher list
                format. If no cipher can be selected (because compile-time options
                or other configuration forbids use of all the specified ciphers),
                an ssl.SSLError will be raised. See ssl.SSLContext.set_ciphers
            api_version (tuple): Specify which Kafka API version to use. If set to
                None, the client will attempt to infer the broker version by probing
                various APIs. Example: (0, 10, 2). Default: None
            api_version_auto_timeout_ms (int): number of milliseconds to throw a
                timeout exception from the constructor when checking the broker
                api version. Only applies if api_version set to None.
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
                        type(topic).__name__
                    )
                )
            if isinstance(topic, str):
                topic = str(topic)
        else:
            raise ValueError(
                f"Sorry, the `topic` parameter is required. Please enter topic value parameter."
            )

        if run is not None:
            if not isinstance(run, str):
                raise TypeError(
                    "Invalid \"Producer\" parameter, value must be type str, {} passed".format(
                        type(run).__name__
                    )
                )
            if isinstance(run, str):
                run = str(run)
        else:
            raise ValueError(
                f"Sorry, the `run` parameter is required. Please enter run value parameter."
            )
        self.producer: KafkaProducer = KafkaProducer(
            value_serializer=lambda x: dumps(x)
            .encode('utf-8'),
            **configs
        )
        self.run = run
        # Check whether the topic above already exists in the cluster or not,
        # if it doesn't then a new topic will be created according to the topic name above.
        self.tk: TopicKafka = TopicKafka(
            bootstrap_servers=configs["bootstrap_servers"]
        )
        self.topic = self.tk.newtopic(
            name=topic,
            num_partitions=1,
            replication_factor=1
        )
        self.logger = logging.getLogger(__name__)

    def produser(self, datas: dict):
        """Publish a message to a topic.

        Arguments:
            topic (str): topic where the message will be published
            value (optional): message value. Must be type bytes, or be
                serializable to bytes via configured value_serializer. If value
                is None, key is required and message acts as a 'delete'.
                See kafka compaction documentation for more details:
                https://kafka.apache.org/documentation.html#compaction
                (compaction requires kafka >= 0.8.1)
            partition (int, optional): optionally specify a partition. If not
                set, the partition will be selected using the configured
                'partitioner'.
            key (optional): a key to associate with the message. Can be used to
                determine which partition to send the message to. If partition
                is None (and producer's partitioner config is left as default),
                then messages with the same key will be delivered to the same
                partition (but if key is None, partition is chosen randomly).
                Must be type bytes, or be serializable to bytes via configured
                key_serializer.
            headers (optional): a list of header key value pairs. List items
                are tuples of str key and bytes value.
            timestamp_ms (int, optional): epoch milliseconds (from Jan 1 1970 UTC)
                to use as the message timestamp. Defaults to current time.
        """
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
