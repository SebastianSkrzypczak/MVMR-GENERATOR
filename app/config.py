from abc import ABC, abstractmethod
from sqlalchemy import create_engine as sqlalchemy_engine
from google.cloud.sql.connector import Connector, IPTypes
import os


class AbstractDbConfiguration(ABC):

    @abstractmethod
    def create_new_engine():
        pass


class DockerDbConfiguration(AbstractDbConfiguration):

    def create_new_engine():
        uri = os.environ.get("DB_URL")
        return sqlalchemy_engine(uri)


class LocalDbConfiguration(AbstractDbConfiguration):
    def create_db_engine():
        host = os.environ.get("DB_HOST", "localhost")
        port = 5432 if host == "localhost" else 5432
        password = os.environ.get("DB_PASSWORD", "admin")
        user, db_name = "mvmr", "mvmr"
        encoding = "unicode"
        uri = f"postgresql://{user}:{password}@{host}:{port}/{db_name}?client_encoding={encoding}"
        return sqlalchemy_engine(uri)


class CloudDbConfiguration(AbstractDbConfiguration):
    def create_db_engine():
        INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")
        DB_USER = os.environ.get("DB_USER")
        DB_PASS = os.environ.get("DB_PASS")
        DB_NAME = os.environ.get("DB_NAME")
        ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC
        connector = Connector()

        def getconn():
            conn = connector.connect(
                INSTANCE_CONNECTION_NAME,
                "pg8000",
                user=DB_USER,
                password=DB_PASS,
                db=DB_NAME,
                ip_type=ip_type,
            )
            return conn

        pool = sqlalchemy_engine(
            "postgresql+pg8000://",
            creator=getconn,
        )

        return pool


def create_db_engine():
    return CloudDbConfiguration.create_db_engine()


def get_settings_for_random_generation():
    settings = {"max_difference": 10}
    return settings
