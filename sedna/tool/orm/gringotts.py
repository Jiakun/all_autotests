""" The ORM classes and database """

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

from sedna.tool.orm import BaseDAO

Base = declarative_base()


class Bill(Base):
    """ORM object to map gringotts.bill table"""
    __tablename__ = "bill"

    id = Column(Integer, primary_key=True)
    bill_id = Column(String)
    order_id = Column(String)
    resource_id = Column(String)
    status = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    project_id = Column(String)


class Order(Base):
    """ORM object to map gringotts.order table"""
    __tablename__ = "order"

    id = Column(Integer, primary_key=True)
    order_id = Column(String)
    resource_id = Column(String)
    resource_name = Column(String)
    type = Column(String)
    status = Column(String)


class GringottsDAO(BaseDAO):
    """ DAO class to manipulate gringotts datdabase """

    def __init__(self, db_url):
        """
        Class initialization
        :param db_url: url string to connection to the database
        """
        super(GringottsDAO, self).__init__(db_url)

    def get_metaclass(self):
        return Base

    def get_orders(self, resource_id):
        """
        Retrieve orders for the give resource
        :param resource_id: the id of resource whose orders will be queried
        :return: the list of orders of the given resource
        """
        session = self.create_session()
        try:
            return session.query(Order)\
                .filter(Order.resource_id == resource_id).all()
        finally:
            session.close()

    def get_bills(self, order_id):
        """
        Retrieve the bills belonging to the given order
        :param order_id: the id of order whose bills will be retrieved
        :return: the list of the bills belonging to the given order
        """
        session = self.create_session()
        try:
            return session.query(Bill)\
                .filter(Bill.order_id == order_id).all()
        finally:
            session.close()
