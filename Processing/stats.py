from ast import In
from xmlrpc.client import DateTime
from sqlalchemy import Column, Integer, String, DateTime
from base import Base
class Stats(Base):
    """ Processing Statistics """

    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)
    num_orders_total = Column(Integer, nullable=False)
    max_quantity = Column(Integer, nullable=False)
    min_quantity = Column(Integer, nullable=False)
    num_customers_total = Column(Integer, nullable=False)
    last_updated= Column(DateTime, nullable=False)

    def __init__(self, num_orders_total, max_quantity, min_quantity, num_customers_total, last_updated):
        """ Initializes a processing statistics object """
        self.num_orders_total = num_orders_total
        self.max_quantity = max_quantity
        self.min_quantity = min_quantity
        self.num_customers_total = num_customers_total
        self.last_updated = last_updated

    def to_dict(self):
        dict = {}
        dict['num_orders_total'] = self.num_orders_total
        dict['max_quantity'] = self.max_quantity
        dict['min_quantity'] = self.min_quantity
        dict['num_customers_total'] = self.num_customers_total
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:M:S")

        return dict