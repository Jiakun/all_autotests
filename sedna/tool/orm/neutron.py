""" ORM object and database manipulation DAO for neutron """

from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

from sedna.tool.orm import BaseDAO

Base = declarative_base()


class Router(Base):
    """ ORM class for neutron routers table """
    __tablename__ = "routers"

    id = Column(String, primary_key=True)
    name = Column(String)
    tenant_id = Column(String)
    status = Column(String)


class NeutronDAO(BaseDAO):
    """DAO object for neutron database manipulation """

    def __init__(self, db_url):
        """
        Initialization
        :param db_url: database connection url
        """
        super(NeutronDAO, self).__init__(db_url)

    def get_metaclass(self):
        return Base

    def get_routers(self, project_id):
        """
        Retrieving router for the given project.
        :param project_id: the id of the project whose routers will be queried
        :return: the list of routers belonging to the given project
        """
        session = self.create_session()
        try:
            return session.query(Router)\
                    .filter(Router.tenant_id == project_id)\
                    .all()
        finally:
            session.close()
