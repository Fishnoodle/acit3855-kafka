import connexion
from connexion import NoContent
from pykafka import KafkaClient
import pykafka
import yaml
import json
import datetime
from flask_cors import CORS, cross_origin
import logging.config
import logging

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


def get_restaurant_reading(index):
    with open ('app_conf.yaml', 'r') as f:
        app_conf = yaml.safe_load(f.read())
    counter = 0
    hostname = "%s:%d" % (app_conf["kafka"]["hostname"],
                        app_conf["kafka"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_conf["kafka"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                        consumer_timeout_ms=1000)

    


    logger.info("Retrieving Restaurant at index %d" % index)
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
        if msg['type'] == 'Restaurant' and index == counter:
            return msg['payload'], 200
        else:
            counter +=1

    except:
        logger.error("No more messages found")

    logger.error("Could not find Restaurant at index %d" % index)
    return { "message": "Not Found"}, 404


def get_delivery_reading(index):
    with open ('app_conf.yaml', 'r') as f:
        app_conf = yaml.safe_load(f.read())
    
    counter = 0
    hostname = "%s:%d" % (app_conf["kafka"]["hostname"],
                        app_conf["kafka"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_conf["kafka"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                        consumer_timeout_ms=1000)

    logger.info("Retrieving Delivery at index %d" % index)
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'Delivery' and index == counter:
                return msg['payload'], 200
            else: 
                counter +=1
    except:
        logger.error("No more messages found")

    logger.error("Could not find Delivery at index %d" % index)
    return { "message": "Not Found"}, 404

def get_health():
    pass


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/audit_log", strict_validation=True, validate_responses=True)
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'


if __name__ == "__main__":
    app.run(port=8110)
