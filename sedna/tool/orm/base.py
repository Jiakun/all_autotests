"""The base class for ORM logic """
from abc import abstractmethod
from exceptions import NotImplementedError

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class BaseDAO(object):
    """Base class for DAO classes """

    _db_engine = None

    def __init__(self, db_url):
        self._db_url = db_url

    @abstractmethod
    def get_metaclass(self):
        """
        The meta data class for the declarative class definitions. There
         should be one such class for each database, which will be used
         for ORM class to inherit
        """
        raise NotImplementedError("get_metaclass")

    def create_session(self):
        """
        Create a new session for a database operation. The session should
        be closed after using.
        :return: A new database session.
        """
        if self._db_engine is None:
            self._db_engine = create_engine(self._db_url)
            self.get_metaclass().bind = self._db_engine

        return sessionmaker(bind=self._db_engine)()
