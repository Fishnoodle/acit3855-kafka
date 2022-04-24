import datetime
from http.client import NO_CONTENT, NotConnected
from multiprocessing import connection
from pdb import Restart
import time
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import json
import yaml
import logging
from logging import config
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from base import Base
import connexion
from stats import Stats
import uuid
import sqlite3
from flask_cors import CORS, cross_origin
from base import Base
from stats import Stats

import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yaml"
    log_conf_file = "/config/log_conf.yaml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yaml"
    log_conf_file = "log_conf.yaml"


with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


if not os.path.isfile(app_config["datastore"]["filename"]):
    connection = sqlite3.connect(app_config["datastore"]["filename"])
    conn = connection.cursor()

    conn.execute('''
                CREATE TABLE stats
                (id INTEGER PRIMARY KEY ASC,
                num_orders_total INTEGER NOT NULL,
                max_quantity INTEGER NOT NULL,
                min_quantity INTEGER NOT NULL,
                num_customers_total INTEGER NOT NULL,
                last_updated VARCHAR(100) NOT NULL)
                ''')
    
    connection.commit()
    connection.close()


DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def populate_stats():
    global num_orders_total
    logger.info("Periodic Processing Starting")
    trace_id = uuid.uuid1()
    session = DB_SESSION()

    var = session.query(Stats).order_by(Stats.last_updated.desc()).first()

    current_timestamp = str(datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S"))
    end_date = str(datetime.datetime.strftime(var.last_updated, "%Y-%m-%d %H:%M:%S"))

    logger.info("TIMELINE FOR STATISTICS \n -----------------------")
    logger.info("From: " + end_date + " - - - To: " + current_timestamp) 
    
    last_updated = datetime.datetime.now()

    delivery_get_response = requests.get("http://bcitacit3855.westus.cloudapp.azure.com/storage/request/delivery", params={'timestamp': end_date, 'end_date': current_timestamp})
    if delivery_get_response.ok:
        logger.info(f"{delivery_get_response} received response -- Delivery")
    else:
        logger.error(f"{delivery_get_response} not received -- Delivery")
        return 404


    restaurant_get_response = requests.get("http://bcitacit3855.westus.cloudapp.azure.com/storage/request/restaurant", params={'timestamp': end_date, 'end_date': current_timestamp})
    if restaurant_get_response.ok:
        logger.info(f"{restaurant_get_response} received response -- Restaurant")
    else:
        logger.error(f"{restaurant_get_response} not received -- Restaurant")
        return 404

    logger.info("RESTAURANT RESULTS")
    logger.info(restaurant_get_response.json())
    logger.info("DELIVERY RESULTS")
    logger.info(delivery_get_response.json())

    try:
        restaurant_results = restaurant_get_response.json()[0]
    except:
        restaurant_results = {
            "customer_id": "e370c25c-118d-11ec-82a8-0242ac130003",
            "food_order": {
                "item_id": 21,
                "price": 3292,
                "quantity": 1
            },
            "order_id": "0034829",
            "time_stamp": "2021-6-23T15:12:43"
            }

    try:
        delivery_results = delivery_get_response.json()[0]
    except:
        delivery_results = {
            "food_order": {
                "item_id": 21,
                "price": 329200,
                "quantity": 1
            },
            "order_address": "3842 23rd Street Vancouver FJ2KLS",
            "order_id": "003482",
            "pickup_address": "Resturant Name - 4328 Elmer Street Burnaby FJ592JF"
            }

    logger.debug(restaurant_results)

    #CALCULATIONS
    max_quantity = var.max_quantity
    min_quantity = var.min_quantity
    num_orders_total = var.num_orders_total + 1
    num_customers_total = var.num_customers_total + 1


    if restaurant_results['food_order']['quantity'] > max_quantity:
        max_quantity = restaurant_results['food_order']['quantity']
    elif delivery_results['food_order']['quantity'] > max_quantity:
        maax_quantity = delivery_results['food_order']['quantity']

    if restaurant_results['food_order']['quantity'] < min_quantity:
        min_quantity = restaurant_results['food_order']['quantity']
    elif delivery_results['food_order']['quantity'] < min_quantity:
        min_quantity = delivery_results['food_order']['quantity']


    stats = Stats(num_orders_total,
                max_quantity,
                min_quantity,
                num_customers_total,
                last_updated
    )

    logger.info("Periodic Processing Finished")
    session.add(stats)
    try:
        session.commit()
    except:
        session.rollback()
    session.close()
    pass

def get_stats():
    session = DB_SESSION()

    try:
        stats = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    except:
        return NoContent, 400

    session.close()

    logger.info(stats.to_dict())
    return stats.to_dict(), 201

def get_health():
    pass


def init_scheduler():
    sched = BackgroundScheduler(daemon=True, job_defaults={'max_instances': 2})
    sched.add_job(populate_stats,
                    'interval',
                    seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            base_path="/processing",
            strict_validation=True,
            validate_responses=True)
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'


if __name__ == "__main__":
    # run our standalone gevent server
    init_scheduler()
    app.run(port=8100, use_reloader=False)
