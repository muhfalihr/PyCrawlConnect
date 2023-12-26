# INSTALLATION & CONFIGURATION KAFKA AND KAFKA MANAGER UI

![](https://www.unosquare.com/wp-content/uploads/2019/07/Unosquare_81-1024x325.webp)

## I. Kafka installation and configuration

- Open a VM specific to Kafka Server.

- Downloaded Kafka version 3.2.0 archive file in tgz format. See the [official Apache Kafka site](https://kafka.apache.org/downloads).

  ```sh
  wget https://archive.apache.org/dist/kafka/3.2.0/kafka_2.13-3.2.0.tgz
  ```

- Extract archive files in tar.gz format.

  ```sh
  tar -xzf kafka_2.13-3.2.0.tgz
  ```

  Information:

  - **-x :** Extraction
  - **-z :** Uses gzip compression
  - **-f :** Specifies the archive file name (in this case, kafka_2.13-3.2.0.tgz)

- install Java version 11, because Kafka uses the Java programming language

  ```sh
  # Install Java
  sudo apt install openjdk-11-jdk

  # Check Java version
  java -version
  ```

- Changing Kafka data directory. **(Optional)**

  ```sh
  # create a data folder in the Kafka directory.
  mkdir -p kafka_2.13-3.2.0/data

  # Edit the server.properties configuration file
  nano kafka_2.13-3.2.0/config/server.properties

  ## log.dirs=/tmp/kafka-logs --> log.dirs=data

  # Create CLUSTER ID
  kafka_2.13-3.2.0/bin/kafka-storage.sh random-uuid

  # The new data directory format is created and configured
  kafka_2.13-3.2.0/bin/kafka-storage.sh format --cluster-id <CLUSTER-ID> --config kafka_2.13-3.2.0/config/server.properties
  ```

## II. Kafka Manager UI Installation and Setup

- Clonig Repository with Git

  ```sh
  git clone https://github.com/yahoo/CMAK.git
  ```

- Change directory

  ```sh
  cd CMAK/
  ```

- Cleaning up the Scala project (using sbt) and creating a distribution (package) of the project.

  ```sh
  ./sbt clean dist
  ```

- Change directory

  ```sh
  cd CMAK/target/universal
  ```

- Install unzip

  ```sh
  apt install unzip
  ```

- Extract (unzip) archive files.

  ```sh
  unzip cmak-*.zip
  ```
