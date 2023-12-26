# INSTALLATION & CONFIGURATION ELASTICSEARCH AND KIBANA

## I. Installation Elasticsearch

- Open a VM specific to Elasticsearch Server.

- Download the GPG (GNU Privacy Guard) key from the URL https://artifacts.elastic.co/GPG-KEY-elasticsearch, then decode it and save it as the file **/usr/share/keyrings/elastic.gpg**.

  ```sh
  curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | gpg --dearmor -o /usr/share/keyrings/elastic.gpg
  ```

- Added Elasticsearch repository version 7.x to the list of package sources.

  ```sh
  echo "deb [signed-by=/usr/share/keyrings/elastic.gpg] https://artifacts.elastic.co/packages/7.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-7.x.list
  ```

- Updated the package list.

  ```sh
  apt update
  ```

- Installed Elasticsearch version 7.17.15.

  ```sh
  apt install elasticsearch=7.17.15
  ```

## II. Configuration Elasticsearch

- Edit the elasticsearch.yml configuration file.

  ```sh
  nano /etc/elasticsearch/elasticsearch.yml
  ```

  ```
  cluster.name: ClusterName
  node.name: nodename
  path.data: /var/lib/elasticsearch/
  path.logs: /var/log/elasticsearch/
  path.home: /usr/share/elasticsearch/
  network.host: 192.168.57.8
  http.port: 9200
  discovery.type: single-node
  ```

- Edit the jvm.options file.

  ```sh
  nano /etc/elasticsearch/jvm.options
  ```

  ```
  -Xmx128m
  -Xms128m
  ```

  Informations: The maximum value is 50% of the server RAM.

  - **Xmx :** Maximum Hipe Space.
  - **Xms :** Initial Hipe Space.

## III. Set Authentication Elasticsearch

- Create a new folder in the Elasticsearch directory with the name **config**.

  ```sh
  mkdir -p /etc/elasticsearch/config
  ```

- Create a certificate authority for your Elasticsearch cluster

  ```sh
  /usr/share/elasticsearch/bin/elasticsearch-certutil ca

  # Then press ENTER and ENTER again.

  /usr/share/elasticsearch/bin/elasticsearch-certutil cert --ca elastic-stack-ca.p12

  # Then press ENTER, ENTER and ENTER again.
  ```

- Added permission to read certificates.

  ```sh
  chmod +r /usr/share/elasticsearch/elastic-stack-ca.p12
  ```

- Copy the certificate into the /etc/elasticsearch/config/ directory.

  ```sh
  cp /usr/share/elasticsearch/elastic-stack-ca.p12 /etc/elasticsearch/config/

  cp /usr/share/elasticsearch/elastic-certificates.p12 /etc/elasticsearch/config/
  ```

- Edit the elasticsearch.yml configuration file.

  ```sh
  nano /etc/elasticsearch/elasticsearch.yml
  ```

  Add configuration:

  ```
  xpack.security.enabled: true
  xpack.security.transport.ssl.enabled: true
  xpack.security.transport.ssl.verification_mode: certificate
  xpack.security.transport.ssl.keystore.path: config/elastic-certificates.p12
  xpack.security.transport.ssl.truststore.path: config/elastic-certificates.p12
  ```

- Recursively change ownership of files and directories (including files and directories in subdirectories).

  ```sh
  chown -R elasticsearch: /etc/elasticsearch/*
  ```

- Restart Elasticsearch service

  ```sh
  systemctl restart elasticsearch.service
  ```

- Setting password for Elasticsearch node authentication.

  ```sh
  /usr/share/elasticsearch/bin/elasticsearch-setup-passwords interactive
  ```

- Run the elasticsearch service

  ```sh
  systemctl start elasticsearch.service
  ```

- Making requests using the curl tool to the Elasticsearch Cluster.

  ```sh
  curl -u elastic:password 192.168.57.8:9200
  ```

  Informations:

  - **elastic**: is the default username of elasticsearch itself.
  - **password**: The password you used was previously setup-password.

- If successful, the response will be like this:

  ```
  root@singlenode:~# curl 192.168.57.8:9200
  {
  "name": "nodename",
  "cluster_name": "SingleName",
  "cluster_uuid": "GMacEg2kRtyUJJs04lwP6Q",
  "version" : {
  "number": "7.17.15",
  "build_flavor": "default",
  "build_type": "deb",
  "build_hash": "0b8ecfb4378335f4689c4223d1f1115f16bef3ba",
  "build_date": "2023-11-10T22:03:46.9873990162",
  "build_snapshot": false,
  "lucene_version": "8.11.1",
  "minimum_wire_compatibility_version": "6.8.0",
  "minimum_index_compatibility_version": "6.0.0-beta1"
  },
  "tagline" : "You Know, for Search"
  }
  root@singlenode:~#
  ```

## IV. Installation KIBANA

- Install Kibana with apt.

  ```sh
  apt install kibana=7.17.15

  # Note: The installed version of Kibana must be the same as the installed version of elasticsearch.
  ```

- Edit the kibana.yml configuration file.

  ```sh
  nano /etc/kibana/kibana.yml
  ```

  ```
  server.port: 5601
  server.host: "192.168.57.8"
  server.name: "nodename"
  elasticsearch.hosts: ["http://192.168.57.8:9200"]
  elasticsearch.username: "elastic"
  elasticsearch.password: "password"
  ```

- Restart Kibana service.

  ```sh
  systemctl restart kibana.service
  ```

- Run the Kibana service.

  ```sh
  systemctl start kibana.service
  ```

- To run Kibana UI you have to open a browser, then type kibana hosts in the kibana.yml file earlier.

  ```
  http://192.168.57.8:5601

  If the login form appears, it means that your installation and configuration of Kibana has been successful.
  But if "Kibana server is not yet" appears, this means the installation failed (make sure the configuration is correct).
  ```

# NOTE : The configuration and setup above is only used for single-nodes, not for multi-nodes!!!!!
