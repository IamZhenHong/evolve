# neo4j_config.py
from neo4j import GraphDatabase, basic_auth
from dotenv import load_dotenv
import os
from neo4j import GraphDatabase, basic_auth
from google.cloud import secretmanager
# Load environment variables from .env file
load_dotenv()

client = secretmanager.SecretManagerServiceClient()

# Define the project and secret information
project_id = "empyrean-button-434915-s8"
secret_id = "evolve"
secret_version = "latest"

# Build the secret version resource name
secret_version_name = f"projects/{project_id}/secrets/{secret_id}/versions/{secret_version}"

# Access the secret version
response = client.access_secret_version(name=secret_version_name)

# Extract the secret payload
secret_payload = response.payload.data.decode("UTF-8")

# Split the secret payload into environment variables
secret_lines = secret_payload.split('\n')
secrets = {}
for line in secret_lines:
    if '=' in line:
        key, value = line.split('=', 1)
        secrets[key] = value

# Extract the variables
uri = secrets.get("NEO4J_URI")
user = secrets.get("NEO4J_USERNAME")
password = secrets.get("NEO4J_PASSWORD")



class Neo4jConnection:
    _driver = None

    @classmethod
    def get_driver(cls):
        if cls._driver is None:
            cls._driver = GraphDatabase.driver(
                uri, auth=basic_auth(user, password))
            
        return cls._driver
