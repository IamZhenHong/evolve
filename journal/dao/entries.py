from neo4j import GraphDatabase
import hashlib
class EntryDAO:
    def __init__(self, driver):
        self.driver = driver

    def list_entries(self, user_id):
        with self.driver.session() as session:
            return session.read_transaction(self._list_entries, user_id)

    @staticmethod
    def _list_entries(tx, user_id):
        query = """
        MATCH (u:User {user_id: $user_id})-[:WROTE]->(e:JournalEntry)
        OPTIONAL MATCH (e)-[:HAS_MOOD]->(m:Mood)
        RETURN id(e) AS node_id, e, m.name AS mood
        """
        result = tx.run(query, user_id=user_id)
        return [{'id': record['node_id'], 'entry': record['e'], 'mood': record.get('mood')} for record in result]

    def view_last_entry(self, user_id):
        with self.driver.session() as session:
            return session.read_transaction(self._view_last_entry_tx, user_id)

    @staticmethod
    def _view_last_entry_tx(tx, user_id):
        query = """
        MATCH (u:User {user_id: $user_id})-[:WROTE]->(e:JournalEntry)
        OPTIONAL MATCH (e)-[:HAS_MOOD]->(m:Mood)
        RETURN id(e) AS node_id, e, m.name AS mood
        ORDER BY e.date_created DESC
        LIMIT 1
        """
        result = tx.run(query, user_id=user_id)
        return [{'id': record['node_id'], 'entry': record['e'], 'mood': record.get('mood')} for record in result]

    def create_journal_entry(self, user_id, summary, cumulative_summary, content, date_created, mood):
        with self.driver.session() as session:
            session.write_transaction(
                self._create_journal_entry_tx, user_id, summary, cumulative_summary, content, date_created, mood
            )

    @staticmethod
    def _create_journal_entry_tx(tx, user_id, summary, cumulative_summary, content, date_created, mood):
        query = """
        MATCH (u:User {user_id: $user_id})
        CREATE (j:JournalEntry {
            summary: $summary, 
            cumulative_summary: $cumulative_summary, 
            content: $content, 
            date_created: $date_created
        })
        MERGE (m:Mood {name: $mood})
        MERGE (j)-[:HAS_MOOD]->(m)
        MERGE (u)-[:WROTE]->(j)
        RETURN j, m
        """
        tx.run(query, user_id=user_id, summary=summary, cumulative_summary=cumulative_summary, content=content, date_created=date_created, mood=mood)

    def get_journal_entries_for_user(self, user_id):
        with self.driver.session() as session:
            return session.read_transaction(self._get_journal_entries_for_user_tx, user_id)

    @staticmethod
    def _get_journal_entries_for_user_tx(tx, user_id):
        query = """
        MATCH (u:User {user_id: $user_id})-[:WROTE]->(j:JournalEntry)
        OPTIONAL MATCH (j)-[:HAS_MOOD]->(m:Mood)
        RETURN j, m.name AS mood
        """
        result = tx.run(query, user_id=user_id)
        return [{'entry': record['j'], 'mood': record.get('mood')} for record in result]

    def delete_journal_entry(self, node_id):
        with self.driver.session() as session:
            session.write_transaction(self._delete_journal_entry_tx, node_id)

        
    @staticmethod
    def _delete_journal_entry_tx(tx, node_id):
        # Match the JournalEntry by its node ID and delete it
        query = """
        MATCH (e:JournalEntry)
        WHERE id(e) = $node_id
        OPTIONAL MATCH (e)-[r:HAS_MOOD]->(m:Mood)
        DETACH DELETE e
        """
        tx.run(query, node_id=node_id)

