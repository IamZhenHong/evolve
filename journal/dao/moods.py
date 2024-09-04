from neo4j import GraphDatabase

class MoodDAO:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_mood(self, mood_name):
        with self.driver.session() as session:
            result = session.write_transaction(self._create_mood_node, mood_name)
            return result

    @staticmethod
    def _create_mood_node(tx, mood_name):
        query = """
        CREATE (m:Mood {name: $mood_name})
        RETURN m
        """
        result = tx.run(query, mood_name=mood_name)
        return result.single()["m"]

    def get_mood(self, mood_name):
        with self.driver.session() as session:
            result = session.read_transaction(self._get_mood_node, mood_name)
            return result

    @staticmethod
    def _get_mood_node(tx, mood_name):
        query = """
        MATCH (m:Mood {name: $mood_name})
        RETURN m
        """
        result = tx.run(query, mood_name=mood_name)
        return result.single()["m"] if result.single() else None

    def list_all_moods(self):
        with self.driver.session() as session:
            result = session.read_transaction(self._list_all_moods)
            return result

    @staticmethod
    def _list_all_moods(tx):
        query = """
        MATCH (m:Mood)
        RETURN m
        ORDER BY m.name
        """
        result = tx.run(query)
        return [record["m"] for record in result]

    def delete_mood(self, mood_name):
        with self.driver.session() as session:
            result = session.write_transaction(self._delete_mood_node, mood_name)
            return result

    @staticmethod
    def _delete_mood_node(tx, mood_name):
        query = """
        MATCH (m:Mood {name: $mood_name})
        DETACH DELETE m
        """
        tx.run(query)

    def update_mood_name(self, old_name, new_name):
        with self.driver.session() as session:
            result = session.write_transaction(self._update_mood_node, old_name, new_name)
            return result

    @staticmethod
    def _update_mood_node(tx, old_name, new_name):
        query = """
        MATCH (m:Mood {name: $old_name})
        SET m.name = $new_name
        RETURN m
        """
        result = tx.run(query, old_name=old_name, new_name=new_name)
        return result.single()["m"]

