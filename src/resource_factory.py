from logger import Logger, LogType
import sqlite3
import os

class ResourceFactory:
    logger: Logger = None

    def get_logger():
        if ResourceFactory.logger is None:
            ResourceFactory.logger = Logger()
        return ResourceFactory.logger
    
    def get_db_connection() -> sqlite3.Connection:
        try:
            db_path = os.getenv("SQLITE_DB_PATH")
            if db_path is None:
                ResourceFactory.get_logger().log(f"No DB path found in env file, creating the db file in the current directory: {os.curdir}")
                return sqlite3.connect(os.path.join(os.curdir, "motogp.db"))
            return sqlite3.connect(db_path) 
        except Exception as e:
            ResourceFactory.get_logger("Error connecting to the DB", LogType.ERROR)
            raise e
        