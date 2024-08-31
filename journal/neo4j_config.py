# neo4j_config.py
from neo4j import GraphDatabase, basic_auth
from dotenv import load_dotenv
import os
from neo4j import GraphDatabase, basic_auth

# Load environment variables from .env file
load_dotenv()

# Get environment variables
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")


class Neo4jConnection:
    _driver = None

    @classmethod
    def get_driver(cls):
        if cls._driver is None:
            cls._driver = GraphDatabase.driver(
                uri, auth=basic_auth(user, password))
            
        return cls._driver
