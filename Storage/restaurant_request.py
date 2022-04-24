from decimal import Decimal
from os import times
from sqlite3 import IntegrityError
from sqlite3.dbapi2 import Timestamp
from tokenize import Double
import uu
import uuid
from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class RestaurantRequest(Base):
    """ Restaurant Request """

    __tablename__ = "restaurant"

    id = Column(Integer, primary_key=True)
    order_id = Column(String(250), nullable=False)
    customer_id = Column(String(250), nullable=False)
    item_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    time_stamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(250), nullable=True)

    def __init__(self, order_id, customer_id, item_id, quantity, price, time_stamp, trace_id):
        """ Initializes a restaurant request """
        self.order_id = order_id
        self.customer_id = customer_id
        self.item_id = item_id
        self.quantity = quantity
        self.price = price
        self.time_stamp = time_stamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.trace_id = uuid.uuid1()
    
    def to_dict(self):
        """ Dictionary Representation of a restaurant request """
        dict = {}
        dict['id'] = self.id
        dict['order_id'] = self.order_id
        dict['customer_id'] = self.customer_id
        dict['food_order'] = {}
        dict['food_order']['item_id'] = self.item_id
        dict['food_order']['quantity'] = self.quantity
        dict['food_order']['price'] = self.price
        dict['time_stamp'] = self.time_stamp
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id
        
        return dict
