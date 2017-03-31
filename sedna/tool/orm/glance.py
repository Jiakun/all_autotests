""" ORM and DAO for glance tables """

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sedna.tool.orm import BaseDAO

Base = declarative_base()


class Image(Base):
    """ ORM class for images table"""
    __tablename__ = "images"

    id = Column(String, primary_key=True)
    status = Column(String)
    deleted = Column(Integer)
    owner = Column(String)
    properties = relationship("ImageProperty", back_populates="image")


class ImageProperty(Base):
    """ ORM class for image_properties table """
    __tablename__ = "image_properties"

    id = Column(Integer, primary_key=True)
    image_id = Column(String, ForeignKey("images.id"))
    name = Column(String)
    value = Column(String)
    image = relationship("Image", back_populates="properties")


class GlanceDAO(BaseDAO):
    """ DAO for glance database manipulation """

    def __init__(self, db_url):
        """
        Initialization
        :param db_url: database connection url
        """
        super(GlanceDAO, self).__init__(db_url)

    def get_metaclass(self):
        return Base

    def get_images(self, project_id):
        """
        Retrieving images of the given project.
        :param project_id: the project id whose images will be retrieved.
        :return: SQLAlchemy Query object for Images
        # TODO convert return result from query to list
        """
        session = self.create_session()
        try:
            return session.query(Image).filter(Image.owner == project_id)
        finally:
            session.close()

    def get_snapshots(self, project_id):
        """
        Retrieving images used as vm snapshot for the given project.
        :param project_id: the project id whose snapshot will be retrieved.
        :return: SQLAlchemy Query object for snapshots
        # TODO convert return result from query to list
        """
        session = self.create_session()
        try:
            return session.query(Image).join(ImageProperty)\
                .filter(Image.owner == project_id)\
                .filter(ImageProperty.value == "snapshot")
        finally:
            session.close()
