from gzip import READ
from inspect import trace
import uu
import connexion 
from connexion import NoContent
import json
import os
import yaml
import requests 
import logging 
import logging.config
import datetime
import json
import os.path
import uuid
import time
from pykafka import KafkaClient
from flask_cors import CORS, cross_origin
from pykafka.exceptions import SocketDisconnectedError, LeaderNotAvailable


import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yaml"
    log_conf_file = "/config/log_conf.yaml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yaml"
    log_conf_file = "log_conf.yaml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")

logger.info("App Conf File: %s" % app_config) 
logger.info("Log Conf File: %s" % log_config)


def report_restaurant_request(body):
    logger.info(f"Received event report_restaurant_request")

    retry_count = 1
    max_retry = app_config["connecting_kafka"]["retry_count_max"]
    while retry_count <= max_retry:
        logger.info(f"Attempting to Connect. Retry count is: {retry_count}")
        try:
            hostname = "%s:%d" % (app_config["events"]["hostname"],
                    app_config["events"]["port"])
            logger.info(hostname)
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            logger.info("Connected")
            retry_count = 1000
        except:
            logger.error("Retrying Connection")
            time.sleep(app_config["connecting_kafka"]["time_sleep"])
            retry_count += 1
    msg = {
        "type": 'Restaurant',
        "datatime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payload": body
    }
    producer = topic.get_sync_producer()
    msg_str = json.dumps(msg)
    try:
        producer.produce(msg_str.encode('utf-8'))
    except (SocketDisconnectedError, LeaderNotAvailable) as e:
        producer = topic.get_producer()
        producer.stop()
        producer.start()
        producer.produce(msg_str.encode('utf-8'))

    return NoContent, 201


def report_delivery_request(body):
    logger.info(f"Received event report_delivery_request")

    retry_count = 1
    max_retry = app_config["connecting_kafka"]["retry_count_max"]
    while retry_count <= max_retry:
        logger.info(f"Attempting to Connect. Retry count is: {retry_count}")
        try:
            hostname = "%s:%d" % (app_config["events"]["hostname"],
                    app_config["events"]["port"])
            logger.info(hostname)
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            logger.info("Connected")
            retry_count = 1000
        except:
            logger.error("Retrying Connection")
            time.sleep(app_config["connecting_kafka"]["time_sleep"])
            retry_count += 1
    msg = {
        "type": 'Delivery',
        "datatime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payload": body
    }
    logger.info(msg)
    producer = topic.get_sync_producer()
    msg_str = json.dumps(msg)
    try:
        producer.produce(msg_str.encode('utf-8'))
    except (SocketDisconnectedError, LeaderNotAvailable) as e:
        producer = topic.get_producer()
        producer.stop()
        producer.start()
        producer.produce(msg_str.encode('utf-8'))

    return NoContent, 201




def get_health():
    pass

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            base_path="/receiver",
            strict_validation=True,
            validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'


if __name__ == "__main__":
    app.run(port=8080)
