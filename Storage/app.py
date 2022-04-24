from inspect import trace
from sqlite3 import Timestamp
import connexion
from connexion import NoContent
import yaml
import logging.config
import logging
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from restaurant_request import RestaurantRequest
from delivery_request import DeliveryRequest
from datetime import datetime
import time

import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from flask_cors import CORS, cross_origin
from sqlalchemy import and_

import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yaml"
    log_conf_file = "/config/log_conf.yaml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yaml"
    log_conf_file = "log_conf.yaml"

"""
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
"""

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

with open('app_conf.yaml','r') as f:
    app_config = yaml.safe_load(f)

with open('log_conf.yaml','r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("basicLogger")

database_config = app_config['database_config']


DB_ENGINE = create_engine(
                'mysql+pymysql://' + database_config["user"] +
                ":" + database_config["password"] +
                "@" + database_config["hostname"] +
                ":" + str(database_config["port"]) +
                "/" + database_config["db"]
                        )



Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def report_delivery_request(body):
    """ Receives a delivery request """
    trace_id = uuid.uuid1()

    session = DB_SESSION()

    dr = DeliveryRequest(body['order_id'],
                            body['food_order']['item_id'],
                            body['food_order']['price'],
                            body['food_order']['quantity'],
                            body['pickup_address'],
                            body['order_address'],
                            trace_id)

    session.add(dr)

    session.commit()
    session.close()
    logger.debug("Stored event <delivery> request with a trace id of " + str(trace_id) + " + ")

    return NoContent, 201

def get_delivery_request(timestamp, end_date):
    """ Gets new Delivery Request Readings after the timestamp """
    session = DB_SESSION()
    
    results = session.query(DeliveryRequest).filter(and_(DeliveryRequest.date_created >= timestamp, DeliveryRequest.date_created <= end_date))

    results_list = []

    for reading in results:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Session after %s returns %d items" % (timestamp, len(results_list)))
    return results_list, 200


def report_restaurant_request(body):
    """ Receives a delivery request """
    trace_id = uuid.uuid1()

    session = DB_SESSION()

    rr = RestaurantRequest(body['customer_id'],
                            body['food_order']['item_id'],
                            body['food_order']['quantity'],
                            body['food_order']['price'],
                            body['order_id'],
                            body['time_stamp'],
                            trace_id)

    session.add(rr)

    session.commit()
    session.close()
    logger.debug("Stored event <restaurant> request with a trace id of " + str(trace_id) + " + ")

    return NoContent, 201

def get_restaurant_request(timestamp, end_date):
    """ Gets new Restaurant Request Readings after the timestamp """
    session = DB_SESSION()

    results = session.query(RestaurantRequest).filter(and_(RestaurantRequest.date_created >= timestamp, RestaurantRequest.date_created <= end_date))
    print(results)

    results_list = []

    for reading in results:
        results_list.append(reading.to_dict())
        print(results_list)

    session.close()

    logger.info("Session after %s returns %d items" % (timestamp, len(results_list)))
    return results_list, 200

def process_messages():

    topic = retry()

    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                    reset_offset_on_start=False,
                                    auto_offset_reset=OffsetType.LATEST)

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        if msg['type'] == 'Restaurant':
            reading = msg['payload']
            report_restaurant_request(reading)
        elif msg['type'] == 'Delivery':
            reading = msg['payload']
            report_delivery_request(reading)

        consumer.commit_offsets()


def retry():
    retry_num = 1
    max_retry = app_config["connecting_kafka"]["retry_count_max"]
    while retry_num <= max_retry:
        
        logger.info(f"Attempting to connect: {retry_num} out of {max_retry} retries")
        
        try:
            hostname = "%s:%d" % (app_config["events"]["hostname"],   
                                app_config["events"]["port"]) 
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            retry_num = 9001
        except:
            logger.error("Connection Terminated. Retrying...")
            time.sleep(app_config['retries']['sleep'])
            retry_num += 1
    return 


def get_health():
    pass

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/storage", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()    
    app.run(port=8090)
