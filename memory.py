import sqlite3
from datetime import datetime
import dateutil.parser
from typing import Optional, Dict, Any, List, Tuple

class ShortTermMemory:
    def __init__(self):
        self.context: Dict[str, Any] = {}

    def add_context(self, key: str, value: Any) -> None:
        """Add a key-value pair to short-term memory."""
        self.context[key] = value

    def get_context(self, key: str) -> Optional[Any]:
        """Retrieve value by key from short-term memory."""
        return self.context.get(key)

    def clear_context(self) -> None:
        """Clear all short-term memory."""
        self.context.clear()

class LongTermMemory:
    def __init__(self, db_path: str = "memory.db"):
        """Initialize SQLite database for long-term memory."""
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self) -> None:
        """Create creations table if it doesn't exist."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS creations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    original_prompt TEXT,
                    enhanced_prompt TEXT,
                    image_path TEXT,
                    model_path TEXT
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def save_creation(self, original_prompt: str, enhanced_prompt: str, 
                     image_path: str, model_path: str) -> None:
        """Save a creation to long-term memory."""
        try:
            timestamp = datetime.now().isoformat()
            self.cursor.execute("""
                INSERT INTO creations (timestamp, original_prompt, enhanced_prompt, image_path, model_path)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, original_prompt, enhanced_prompt, image_path, model_path))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving creation: {e}")

    def get_creation_by_date(self, date_str: str) -> List[Tuple]:
        """Retrieve creations closest to the given date."""
        try:
            # Handle 'now' as a special case
            if date_str.lower() == 'now':
                target_date = datetime.now()
            else:
                target_date = dateutil.parser.parse(date_str, fuzzy=True).replace(tzinfo=None)
            
            self.cursor.execute("""
                SELECT * FROM creations
                ORDER BY ABS(JULIANDAY(timestamp) - JULIANDAY(?))
                LIMIT 1
            """, (target_date.isoformat(),))
            return self.cursor.fetchall()
        except (ValueError, sqlite3.Error) as e:
            print(f"Error retrieving creation by date: {e}")
            return []

    def get_all_creations(self) -> List[Tuple]:
        """Retrieve all creations sorted by timestamp."""
        try:
            self.cursor.execute("SELECT * FROM creations ORDER BY timestamp DESC")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving all creations: {e}")
            return []

    def __del__(self):
        """Close database connection."""
        try:
            self.conn.close()
        except sqlite3.Error as e:
            print(f"Error closing database: {e}")

if __name__ == "__main__":
    # Test ShortTermMemory
    stm = ShortTermMemory()
    stm.add_context("last_prompt", "Create a robot")
    print("ShortTermMemory test:", stm.get_context("last_prompt"))
    stm.clear_context()
    print("ShortTermMemory cleared:", stm.get_context("last_prompt"))

    # Test LongTermMemory
    ltm = LongTermMemory()
    ltm.save_creation("Create a robot", "A futuristic robot with LED lights", 
                     "outputs/robot.png", "outputs/robot.obj")
    creations = ltm.get_creation_by_date("now")
    print("LongTermMemory test (by date):", creations)
    all_creations = ltm.get_all_creations()
    print("LongTermMemory test (all):", all_creations)
