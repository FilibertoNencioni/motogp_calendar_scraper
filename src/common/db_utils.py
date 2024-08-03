from sqlite3 import Cursor
from common.resource_factory import ResourceFactory
from common.logger import LogType
import datetime

class DbUtils:
    
    def check_if_has_table(cursor:Cursor, table_name: str) -> bool:
        #Controlla se sul DB esiste la tabella
        sql = f"""
            SELECT name 
            FROM sqlite_master 
            WHERE name = ?
        """

        try:
            res = cursor.execute(sql, [table_name])
            return res.fetchone() is not None
        except Exception as e:
            msg = "Error checking if a table exist\n"
            msg += f"\t\tsql: {sql}"
            msg += f"\t\ttable_name: {table_name}"
            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise e


    def check_tables(cursor: Cursor) -> None:
        sql = ""
        try:
            #TABELLA "GRAND_PRIX"
            if not DbUtils.check_if_has_table(cursor, "GRAND_PRIX"):
                sql = """
                    CREATE TABLE GRAND_PRIX(
                        PK_GRAND_PRIX INTEGER PRIMARY KEY NOT NULL,
                        NAME TEXT NOT NULL,
                        YEAR INTEGER NOT NULL
                    );
                """
                cursor.execute(sql)

            #TABELLA "GRAND_PRIX_EVENT"
            if not DbUtils.check_if_has_table(cursor, "GRAND_PRIX_EVENT"):
                sql = """
                    CREATE TABLE GRAND_PRIX_EVENT(
                        PK_GRAND_PRIX_EVENT INTEGER PRIMARY KEY NOT NULL,
                        FK_GRAND_PRIX INTEGER,
                        NAME TEXT NOT NULL,
                        DATE TIMESTAMP NOT NULL,
                        IS_LIVE INTEGER NOT NULL,
                        FOREIGN KEY (FK_GRAND_PRIX) 
                        REFERENCES GRAND_PRIX(PK_GRAND_PRIX) 
                            ON DELETE CASCADE 
                            ON UPDATE NO ACTION
                    );
                """
                cursor.execute(sql)

        except Exception as e:
            msg = "Error during the check and creation of tables\n"
            msg += f"\t\tsql (possibily empty): {sql}"
            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise e
        

    def check_if_has_grand_prix_this_year(cursor: Cursor, gp_name:str)->bool:
        try:
            current_year = datetime.datetime.now().year
            sql = """
                SELECT NAME
                FROM GRAND_PRIX
                WHERE 
                    NAME = ?
                    AND YEAR = ? 
            """
            res = cursor.execute(sql, [gp_name, current_year])
            return res.fetchone() is not None 

        except Exception as e:
            msg = "Error while checking if a grand prix already exists in the DB\n"
            msg += f"\t\tgp_name: {gp_name}"
            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise e
        
    def get_pk_gp_from_name_this_year(cursor: Cursor, gp_name:str)->int:
        try:
            current_year = datetime.datetime.now().year
            sql = """
                SELECT PK_GRAND_PRIX
                FROM GRAND_PRIX
                WHERE 
                    NAME = ?
                    AND YEAR = ? 
            """
            res = cursor.execute(sql, [gp_name, current_year])
            return res.fetchone()[0]

        except Exception as e:
            msg = "Error while getting a this year grand prix by name\n"
            msg += f"\t\tgp_name: {gp_name}"
            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise e
        
    def insert_gp(cursor: Cursor, gp_name:str)->int:
        try:
            current_year = datetime.datetime.now().year
            sql = """
                INSERT INTO GRAND_PRIX
                (
                    NAME,
                    YEAR                
                )
                VALUES (?,?)
            """
            cursor.execute(sql, [gp_name, current_year])
            
            #Una volta inserito recupero la sua PK
            return DbUtils.get_pk_gp_from_name_this_year(cursor, gp_name)

        except Exception as e:
            msg = "Error while inserting a new GP for this year\n"
            msg += f"\t\tgp_name: {gp_name}"
            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise e

    def check_if_event_exists(cursor: Cursor, pk_gp:int, event_name:str, date, is_live:bool)->bool:
        try:
            sql = """
                SELECT NAME
                FROM GRAND_PRIX_EVENT
                WHERE 
                    FK_GRAND_PRIX = ?
                    AND NAME = ?
                    AND DATE = ?
                    AND IS_LIVE = ? 
            """
            res = cursor.execute(sql, [pk_gp, event_name, date, is_live])
            return res.fetchone() is not None

        except Exception as e:
            msg = "Error while checking if an event for a specific grand prix exists\n"
            msg += f"\t\tpk_gp: {pk_gp}\n"
            msg += f"\t\tevent_name: {event_name}\n"
            msg += f"\t\tdate: {date}\n"
            msg += f"\t\tis_live: {is_live}"
            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise e
        
    def add_event_for_gp_if_not_exists(cursor: Cursor, pk_gp:int, event_name:str, date, is_live: bool)->bool:
        try:
            #Break execution if an event for this GP is found
            if DbUtils.check_if_event_exists(cursor, pk_gp, event_name, date, is_live):
                return False
            
            #Add new
            sql = """
                INSERT INTO GRAND_PRIX_EVENT
                (
                    FK_GRAND_PRIX,
                    NAME,
                    DATE,
                    IS_LIVE
                )
                VALUES (?,?,?,?)
            """
            cursor.execute(sql, [pk_gp, event_name, date, is_live])
            return True
            
        except Exception as e:
            msg = "Error while inserting a new event for a GP (if not exists)\n"
            msg += f"\t\tpk_grand_prix: {pk_gp}\n"
            msg += f"\t\tevent_name: {event_name}\n"
            msg += f"\t\tdate: {date}\n"
            msg += f"\t\tis_live: {is_live}"
            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise e