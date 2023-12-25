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

## Requirements

- **Virtual Machine**
  This application runs on a virtual machine, so before you install the application, you have to prepare the virtual machine first. See [Virtual Machine setup steps](https://github.com/muhfalihr/PyCrawlConnect/blob/master/md/VM.md).

- **Python**
  Already installed Python with version 3.10.12. See the [Installation and Setting up Python](https://github.com/muhfalihr/PyCrawlConnect/blob/master/md/PY.md).

- **Kafka**
  If you want to run this and then send the data to the Kafka Topic then you have to install and run Kafka first. See [How to Install and Run Kafka](https://github.com/muhfalihr/PyCrawlConnect/blob/master/md/KAFKA.md).

- **Elasticsearch**
  If the data consumed by Kafa wants to be forwarded to ElasticSearch, you must install ElasticSearch first. See the Steps to [Install and Configure Elasticsearch](https://github.com/muhfalihr/PyCrawlConnect/blob/master/md/ES.md).

## Clone the repository to your directory

```sh
# Install gh
sudo apt install gh

# Auth gh
gh auth login

# Clonig Repository
gh repo clone muhfalihr/PyCrawlConnect

# Change Directory
cd PyCrawlConnect
```

# WAIT
