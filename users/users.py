from neo4j import GraphDatabase

class UserDAO:
    def __init__(self, driver):
        self.driver = driver
        
    def close(self):
        self.driver.close()

    def create_user(self, user_id):
        with self.driver.session() as session:
            session.write_transaction(self._create_user_tx, user_id)

    @staticmethod
    def _create_user_tx(tx, user_id):
        query = """
        MERGE (u:User {user_id: $user_id})
        RETURN u
        """
        tx.run(query, user_id=user_id)

    # You can add more methods for other operations like fetching user details, updating, etc.
