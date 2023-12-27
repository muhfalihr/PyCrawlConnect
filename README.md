[![Instagram: ____mfr.py](https://img.shields.io/badge/Instagram-Follow%20Me-blue?style=social&logo=instagram)](https://www.instagram.com/_____mfr.py/)

# PyCrawlConnect

![Source: https://twitter.com/chocofy/status/1735925835763531984/photo/1](https://github.com/muhfalihr/mystorage/blob/master/pacar2.jpeg?raw=true)

**Application Description:**

PyCrawlConnect is an application developed using the Python programming language with the aim of connecting data obtained from web crawling to Apache Kafka, and subsequently forwarding this data to Elasticsearch. This application is designed to provide an efficient solution for managing crawled data using cutting-edge technologies.

**Key Features:**

1. **Web Data Crawling:** The application can crawl data from various websites using web scraping techniques or APIs provided by specific sites. The crawling module is designed for flexibility and easy configuration.

2. **Kafka Integration:** PyCrawlConnect features the capability to connect crawled data to Apache Kafka. Kafka is used as middleware to manage message queues, ensuring reliability and fault tolerance in the data delivery process.

3. **Elasticsearch Connector:** After data is generated and sent via Kafka, this application can forward the data to Elasticsearch. This allows users to store and index crawled data in Elasticsearch for easy analysis and search.

4. **Easy Configuration:** PyCrawlConnect is designed with easily configurable settings. Users can quickly adjust crawling settings, Kafka configurations, and Elasticsearch parameters through a structured configuration file.

5. **Comprehensive Documentation:** The project comes with comprehensive documentation that explains installation steps, configuration, and how to use the application. This documentation will assist developers or other users who wish to contribute to or use the application.

6. **Open Source:** PyCrawlConnect is an open-source project available on the GitHub platform. Developers can collaborate, provide feedback, or make contributions through pull requests.

By using PyCrawlConnect, users can easily manage and analyze crawled data from various sources in an efficient and structured manner. This project is expected to provide a reliable solution in the context of real-time web data processing.

## Flowchart PyCrawlConnect

![](https://github.com/muhfalihr/mystorage/blob/master/flow/flow_pycrawlconnect.jpg?raw=true)

## Requirements

- **Virtual Machine**
  This application runs on a virtual machine, so before you install the application, you have to prepare the virtual machine first. See [Virtual Machine Installation & Configuration](https://github.com/muhfalihr/PyCrawlConnect/blob/master/md/VM.md).

- **Python**
  Already installed Python with version 3.10.12. See the [Installation and Setting up Python](https://github.com/muhfalihr/PyCrawlConnect/blob/master/md/PY.md).

- **Kafka**
  If you want to run this and then send the data to the Kafka Topic then you have to install and run Kafka first. See [How to Install and Configuration Kafka](https://github.com/muhfalihr/PyCrawlConnect/blob/master/md/KAFKA.md).

- **Elasticsearch**
  If the data consumed by Kafa wants to be forwarded to ElasticSearch, you must install ElasticSearch first. See the Steps to [Elasticsearch Installation & Configuration](https://github.com/muhfalihr/PyCrawlConnect/blob/master/md/ES.md).

## Clone the repository to your directory

```sh
# Change Directory
cd /home/

# Install gh
sudo apt install gh

# Auth gh
gh auth login

# Clonig Repository
gh repo clone muhfalihr/PyCrawlConnect
```

**NOTE: Perform a clone on the Kafka VM.**

## How to use it ?

### 1. Turn on the Kafka and Elasticsearch VM and log in to the root user.

- Open the **VirtualBox** Software.

  ![](https://github.com/muhfalihr/mystorage/raw/master/vm/1.png?raw=true)

- Select and click the Kafka VM.

- Click **Start**.

  ![](https://github.com/muhfalihr/mystorage/raw/master/vm/Screenshot%20from%202023-12-25%2012-01-17.png?raw=true)

- Select and click the Elasticsearch VM.

- Click **Start**.

  ![](https://github.com/muhfalihr/mystorage/raw/master/vm/Screenshot%20from%202023-12-25%2012-01-17.png?raw=true)

- Type your VM username and password.

  ![](https://github.com/muhfalihr/mystorage/raw/master/vm/18.png?raw=true)

- Switch to superuser account (**root**)

  ```sh
  sudo su
  ```

### 2. Remote Server to Kafka dan Elasticsearch VM.

**Remote Kafka VM.**

- Open your 4 Desktop Terminals.

- SSH into the Kafka VM. Do this in each Terminal.

  ```sh
  ssh root@192.168.57.9
  ```

**Remote Elasticsearch VM**

- Open your 1 Desktop Terminals.

- SSH into the Elasticsearch VM.

  ```sh
  ssh root@192.168.57.8
  ```

### 3. Start the elasticsearch and kibana service.

```sh
# elasticsearch service
systemctl start elasticsearch.service

# elasticsearch service
systemctl start kibana.service
```

### 4. Running Zookeeper and Kafka Server as well as CMAK.

- Change Directory

  ```sh
  cd kafka_2.13-3.2.0/
  ```

- Starting a Zookeeper server in an Apache Kafka environment. Do this at the 1st terminal.

  ```sh
  ./bin/zookeeper-server-start.sh ./config/zookeeper.properties
  ```

- Running Kafka Server. Do this at the 2nd terminal.

  ```sh
  ./bin/kafka-server-start.sh ./config/server.properties
  ```

- Running Kafka UI (CMAK). Do this at the 3rd terminal.

  ```sh
  CMAK/target/universal/cmak-*/bin/cmak
  ```

### 5. Run code for Crawling and Produce using VS code.

- Open your Visual Studio Code.

- Install Extensions Remote - SSH: Editing Configuration Files

  ![](https://github.com/muhfalihr/mystorage/blob/master/vscode/Screenshot%20from%202023-12-26%2012-31-34.png?raw=true)

- Press F1 or Ctrl+Shift+P

- Select and click **Remote-SSH: Connect to Host...**

  ![](https://github.com/muhfalihr/mystorage/blob/master/vscode/Screenshot%20from%202023-12-26%2012-32-06.png?raw=true)

- Click **Add New SSH Host...**

  ![](https://github.com/muhfalihr/mystorage/blob/master/vscode/Screenshot%20from%202023-12-26%2012-33-01.png?raw=true)

- Enter SSH Connection Command

  ![](https://github.com/muhfalihr/mystorage/blob/master/vscode/Screenshot%20from%202023-12-26%2012-33-20.png?raw=true)

- Select **/home/ubuntu/.ssh/config**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vscode/Screenshot%20from%202023-12-26%2012-34-15.png?raw=true)

- A **Host added** pop up will appear at the bottom right. Then click **Connect**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vscode/Screenshot%20from%202023-12-26%2012-34-39.png?raw=true)

- Enter the password for SSH to the host earlier.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vscode/Screenshot%20from%202023-12-26%2012-35-08.png?raw=true)

- Press **Ctrl+Shfit+E** > Click **Open Folder** > Type **/home/PyCrawlConnect/** > Click **OK**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vscode/Screenshot%20from%202023-12-26%2012-54-38.png?raw=true)

- Edit the **.env** file, according to what you want.

- Activate your virtual environment. In this example it is activated from the root directory.

  ```sh
  source .venv/my-venv/bin/activate
  ```

- Run the files apibook.py, apimovie.py, apinews.py.
  NOTE : Run it in a different terminal in VS Code.

  ```sh
  # Terminal 1
  python3 apibook.py

  # Terminal 2
  python3 apimovie.py

  # Terminal 3
  python3 apinews.py
  ```

- Install Extensions Live server

- Open the **index.html** file in the **html** directory. Then click **Go Live** at the bottom right.

### 6. Run the code for Consuming and Logging in Elasticsearch in Terminal Desktop.

- Set up the **.env** file first.

- Run the **kafka_consumer.py** file in the **helper** directory. Do this at the 4th terminal.

  ```sh
  python3 helper/kafka_consumer.py
  ```

### 7. Check the data coming into Elasticsearch.

- Open your browser.
- Type elasticsearch.hosts.
  ```
  http://192.168.57.8:5601
  ```
- Enter your **username** and **password** in the login form. Then press **ENTER**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vscode/1.png?raw=true)

- In the **Management** menu, click **Dev Tools**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vscode/2.png?raw=true)

- Retrieves the specified JSON document from an index.
  ```
  GET <index>/_doc/<_id>
  ```

  ## License

  [MIT License](https://github.com/muhfalihr/PyCrawlConnect/blob/master/LICENSE) - Copyright (c) 2023 Muhammad Falih Romadhoni.
