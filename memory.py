import os
import duckdb
import re
from typing import Any, Dict, List, Optional
from string import punctuation
import warnings

class EntityStore():
    """DuckDB-backed Entity store"""

    session_id: str = "default"
    table_name: str = "entity_store"
    db_file: str = "./Memory/entity_memory.db"

    def __init__(
        self,
        session_id: str = "default",
        db_file: str = "./Memory/entity_memory.db",
        table_name: str = "entity_store",
        *args: Any,
        **kwargs: Any,
    ):
        try:
            import duckdb
        except ImportError:
            raise ImportError(
                "Could not import duckdb python package. "
                "Please install it with `pip install duckdb`."
            )

        super().__init__(*args, **kwargs)

        self.db_file = db_file
        self.session_id = session_id
        self.table_name = table_name

    @property
    def connection(self) -> duckdb.connect:
        return duckdb.connect(database=self.db_file)

    @property
    def full_table_name(self) -> str:
        return f"{self.table_name}_{self.session_id}"

    def _get_connection(self) -> duckdb.connect:
        return duckdb.connect(self.db_file)

    def _create_table_if_not_exists(self, conn: duckdb.connect) -> None:
        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {self.full_table_name} (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """
        with conn:
            conn.execute(create_table_query)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with self._get_connection() as conn:
            self._create_table_if_not_exists(conn)
            query = f"""
                SELECT value
                FROM {self.full_table_name}
                WHERE key = ?
            """
            cursor = self.connection.execute(query, (key,))
            result = cursor.fetchone()
            if result is not None:
                value = result[0]
                return value
            return default

    def set(self, key: str, value: Optional[str]) -> None:
        with self._get_connection() as conn:
            self._create_table_if_not_exists(conn)
            if not value:
                return self.delete(key)
            query = f"""
                INSERT OR REPLACE INTO {self.full_table_name} (key, value)
                VALUES (?, ?)
            """
            self.connection.execute(query, (key, value))

    def delete(self, key: str) -> None:
        with self._get_connection() as conn:
            self._create_table_if_not_exists(conn)
            query = f"""
                DELETE FROM {self.full_table_name}
                WHERE key = ?
            """
            self.connection.execute(query, (key,))

    def exists(self, key: str) -> bool:
        with self._get_connection() as conn:
            self._create_table_if_not_exists(conn)
            query = f"""
                SELECT 1
                FROM {self.full_table_name}
                WHERE key = ?
                LIMIT 1
            """
            cursor = self.connection.execute(query, (key,))
            result = cursor.fetchone()
            return result is not None

    def clear(self) -> None:
        with self._get_connection() as conn:
            query = f"""
                DELETE FROM {self.full_table_name}
            """
            self.connection.execute(query)


class EntityMemory():
    """Memory class for storing information about entities."""

    # Define class-level dictionary to store information about entities.
    entities: Dict[str, Optional[str]] = {}
    # Define key to pass information about entities into prompt.
    memory_key: str = "entities"
    # Define the directory to save the database file
    db_file: str = "./Memory/entity_memory.db"
    store: EntityStore = None

    def __init__(self, session_id: str = "default"):
        """Initialize the memory and load entities from the EntityStore database if it exists."""
        super().__init__()
        self.session_id = session_id
        self.db_file = "./Memory/entity_memory.db"
        self.entities = {}
        if not self.store:
            self.initialize_store()
        self.load_entities()

    def initialize_store(self):
        self.store = EntityStore(session_id=self.session_id, db_file=self.db_file)

    @property
    def memory_variables(self) -> List[str]:
        """Define the variables we are providing to the prompt."""
        return [self.memory_key]

    def update_entities(self, entity: str, entity_text: str) -> None:
        if self.store.exists(entity):
            self.store.delete(entity)
            self.store.set(entity, entity_text)
        else:
            self.store.set(entity, entity_text)

    def load_entities(self):
        """Load entities from the EntityStore database if it exists."""
        # Ensure the directory exists before trying to create it
        directory = os.path.dirname(self.db_file)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        # Load entities from the store
        entities_info = self.store.get(self.store.full_table_name, "")
        if entities_info:
            # Update entities dictionary
            self.entities.update(entities_info)

    def clear(self) -> None:
        return self.entities.clear()

