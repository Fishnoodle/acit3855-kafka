import uuid
from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class DeliveryRequest(Base):
    """ Delivery Request """

    __tablename__ = "delivery"

    id = Column(Integer, primary_key=True)
    order_id = Column(String(250), nullable=False)
    item_id = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    pickup_address = Column(String(250), nullable= False)
    order_address = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(250), nullable=True)


    def __init__(self, order_id, item_id, price, quantity, pickup_address, order_address, trace_id):
        """ Initializes a delivery request """
        self.order_id = order_id
        self.item_id = item_id
        self.price = price
        self.quantity = quantity
        self.pickup_address = pickup_address
        self.order_address = order_address
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.trace_id = uuid.uuid1()

    def to_dict(self):
        """ Dictionary Representation of a restaurant request """
        dict = {}
        dict['id'] = self.id
        dict['order_id'] = self.order_id
        dict['food_order'] = {}
        dict['food_order']['item_id'] = self.item_id
        dict['food_order']['price'] = self.price
        dict['food_order']['quantity'] = self.quantity
        dict['pickup_address'] = self.pickup_address
        dict['order_address'] = self.order_address
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
