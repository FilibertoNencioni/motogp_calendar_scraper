import mysql.connector.abstracts
import mysql.connector.connection
from common.logger import Logger, LogType
import mysql.connector 
import os

class ResourceFactory:
    logger: Logger | None = None

    @staticmethod
    def get_logger():
        if ResourceFactory.logger is None:
            ResourceFactory.logger = Logger()

        return ResourceFactory.logger
    
    @staticmethod
    def get_db_connection() -> mysql.connector.abstracts.MySQLConnectionAbstract:
        #Checking ENV data
        db_host = os.getenv("DB_HOST")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")

        if(db_host is None or db_user is None or db_password is None or db_name is None):
            ResourceFactory.get_logger().log(f"Missing DB env variables\n\t\tDB_HOST: {db_host}\n\t\tDB_USER: {db_user}\n\t\tDB_PASSWORD: {db_password}\n\t\tDB_NAME: {db_name}", LogType.ERROR)
            raise Exception("Missing DB env variables")

        #Connecting to the DB
        cnx = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_name)
        return cnx         