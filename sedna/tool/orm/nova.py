""" ORM table mapping object and nova database manipulation logic """

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from sedna.tool.orm import BaseDAO

Base = declarative_base()


class Instance(Base):
    """ Class mapping to instances table"""
    __tablename__ = "instances"

    id = Column(Integer,  primary_key=True)
    uuid = Column(String)
    display_name = Column(String)
    vm_state = Column(String)
    memory_mb = Column(Integer)
    vcpus = Column(Integer)
    deleted = Column(Integer)
    project_id = Column(String)


class NovaDAO(BaseDAO):

    def __init__(self, db_url):
        """
        Initialization
        :param db_url: database connection url
        """
        super(NovaDAO, self).__init__(db_url)

    def get_metaclass(self):
        return Base

    def get_instances(self, project_id):
        """
        Querying all of the instances belonging to the given project,
        including the deleted ones.
        :param project_id: the id of project whose instances will be
        queired
        :return: the list of the instances belonging to the given project
        """
        session = self.create_session()
        try:
            return session.query(Instance)\
                .filter(Instance.project_id == project_id).all()
        finally:
            session.close()
