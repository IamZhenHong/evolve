
from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def run_query(self, query):
        with self._driver.session() as session:
            result = session.run(query)
            return result.data()

if __name__ == "__main__":
    # Replace 'neo4j://your-ip:7687', 'username', and 'password' with your own details
    uri = 'neo4j://34.124.193.227:7687'
    user = 'neo4j'
    password = 'honghong'

    # Initialize connection
    conn = Neo4jConnection(uri, user, password)

    # Example query to get GDS version
    query = "CALL gds.version()"
    result = conn.run_query(query)
    print("GDS Version:", result)

    # Close the connection
    conn.close()
