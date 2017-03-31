""" The ORM classes for cinder database """

from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

from sedna.tool.orm import BaseDAO

Base = declarative_base()


class Volume(Base):
    """Value object for cinder.volumes table"""
    __tablename__ = "volumes"

    id = Column(String, primary_key=True)
    project_id = Column(String)
    display_name = Column(String)
    status = Column(String)


class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(String, primary_key=True)
    volume_id = Column(String)
    project_id = Column(String)
    status = Column(String)


class CinderDAO(BaseDAO):
    """Database access object for cinder table"""

    def __init__(self, db_url):
        """
        Class initialization
        :param db_url: string url for database connection
        """
        super(CinderDAO, self).__init__(db_url)

    def get_volumes(self, project_id):
        """
        Retrieve all the volumes belonging to the given project, even if the
        volume is already deleted.
        :param project_id: the project whose volumes will be queried.
        :return: the list of volumes belonging to the project
        """
        session = self.create_session()
        try:
            return session.query(Volume)\
                    .filter(Volume.project_id == project_id).all()
        finally:
            session.close()

    def get_snapshots(self, project_id):
        session = self.create_session()
        try:
            return session.query(Snapshot)\
                .filter(Snapshot.project_id == project_id).all()
        finally:
            session.close()

    def get_metaclass(self):
        return Base
