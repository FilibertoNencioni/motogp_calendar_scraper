from typing import List
from mysql.connector.abstracts import MySQLCursorAbstract
from common.enum.broadcaster_enum import BroadcasterEnum
from models.circuit import Circuit
from models.event import Event
from models.category import Category
from models.broadcast import Broadcast
import datetime

class DbUtils:

##GENERAL
    @staticmethod
    def has_official_data_for_season(cursor: MySQLCursorAbstract)->bool:
        sql = """
            SELECT COUNT(*) FROM EVENT
            WHERE SEASON = YEAR(CURRENT_DATE())
        """
        cursor.execute(sql)
        res = cursor.fetchone()[0]
        return res > 0
    
    @staticmethod
    def first_event_date_of_season(cursor: MySQLCursorAbstract) -> datetime.date:
        sql = """
            SELECT
                MIN(START_DATE)
            FROM	
                EVENT
            WHERE 
                SEASON = YEAR(CURRENT_DATE())
                AND IS_DISMISSED = 0
        """
        cursor.execute(sql)
        res = cursor.fetchone()[0]
        return res



##CIRCUIT
    @staticmethod
    def check_circuit(cursor: MySQLCursorAbstract, circuit: Circuit) -> int:
        #Check if exists
        sql = "SELECT PK_CIRCUIT FROM CIRCUIT WHERE GUID = %s "
        cursor.execute(sql, (circuit.guid,))
        res = cursor.fetchone()

        circuit_exists = res is not None
        if circuit_exists:
            #UPDATE DATA - even if it's not changed, except for FLAG and PLACEHOLDER paths
            #those will be updated only if the incoming data is not None
            sql = """
                UPDATE CIRCUIT
                SET
                    NAME = %s,
                    COUNTRY = %s,
                    {u1}
                    {u2}
                    DOU = CURRENT_TIMESTAMP
                WHERE
                    PK_CIRCUIT = %s
            """.format(
                u1 = "FLAG_PATH = %s," if circuit.flag_path is not None else "" ,
                u2 = "PLACEHOLDER_PATH = %s," if circuit.placeholder_path is not None else ""
            )

            data: tuple = (circuit.name, circuit.country,)

            if circuit.flag_path is not None:
                data += (circuit.flag_path,)

            if circuit.placeholder_path is not None:
                data += (circuit.placeholder_path,)

            data += (res[0],)
            cursor.execute(sql, data)
            
            return res[0]
        else:
            #If it doesn't exists insert
            sql = """
                INSERT INTO CIRCUIT
                (GUID, NAME, COUNTRY, FLAG_PATH, PLACEHOLDER_PATH)
                VALUES(%s, %s, %s, %s, %s);
            """
            cursor.execute(sql, (circuit.guid, circuit.name, circuit.country, circuit.flag_path, circuit.placeholder_path))
            return cursor.lastrowid

        
##EVENT
    @staticmethod
    def check_event(cursor: MySQLCursorAbstract, event: Event) -> int:
        #Check if exists
        sql = "SELECT PK_EVENT FROM EVENT WHERE GUID = %s "
        cursor.execute(sql, (event.guid,))
        res = cursor.fetchone()

        circuit_exists = res is not None
        if circuit_exists:
            #UPDATE DATA (even if it's not changed)
            sql = """
                UPDATE EVENT
                SET
                    FK_CIRCUIT = %s,
                    NAME = %s,
                    KIND = %s,
                    SEASON = %s,
                    START_DATE = %s,
                    END_DATE = %s,
                    IS_DISMISSED = 0,
                    DOU = CURRENT_TIMESTAMP
                WHERE
                    PK_EVENT = %s
            """
            cursor.execute(sql, (
                event.fk_circuit, 
                event.name, 
                event.kind, 
                event.season, 
                event.start_date.isoformat(),
                event.end_date.isoformat(), 
                res[0]
            ))
            return res[0]
        else:
            #If it doesn't exists insert
            sql = """
                INSERT INTO EVENT
                    (FK_CIRCUIT, GUID, NAME, KIND, SEASON, START_DATE, END_DATE)
                VALUES
                    (%s,%s,%s,%s,%s,%s,%s)
            """

            cursor.execute(sql, (
                event.fk_circuit, 
                event.guid, 
                event.name, 
                event.kind, 
                event.season, 
                event.start_date.isoformat(), 
                event.end_date.isoformat(),
            ))
            return cursor.lastrowid

    
    @staticmethod
    def get_event_by_date(cursor: MySQLCursorAbstract, date: str) -> Event | None:
        sql = """
            SELECT
                PK_EVENT
                , FK_CIRCUIT
                , GUID
                , NAME
                , KIND
                , SEASON
                , START_DATE
                , END_DATE
                , DOI
                , DOU
            FROM
                EVENT
            WHERE
                %s >= START_DATE
                AND %s <= END_DATE 
            ORDER BY IS_DISMISSED ASC #Prioritize not dismissed events if exists
            LIMIT 1
        """

        cursor.execute(sql, (date, date))
        return Event(*cursor.fetchone())

    @staticmethod
    def dismiss_events(cursor: MySQLCursorAbstract, guids: tuple[str]):
        """This method can be used only for MotoGP data, this will get all the events GUID
        and set those as 'dismissed'"""

        sql = f"""
            UPDATE
                EVENT
            SET
                IS_DISMISSED = 1
            WHERE
                GUID NOT IN ({', '.join(f"'{guid}'" for guid in guids)})
                AND SEASON = YEAR(CURRENT_DATE())
        """
        cursor.execute(sql)

##CATEGORY
    @staticmethod
    def get_all_categories(cursor: MySQLCursorAbstract) -> List[Category]:
        sql = "SELECT * FROM CATEGORY"
        cursor.execute(sql)
        return [Category(*row) for row in cursor.fetchall()]

        
##BROADCAST
    @staticmethod
    def check_broadcast(cursor: MySQLCursorAbstract, broadcast: Broadcast) -> int:
        #Check if exists
        if broadcast.fk_broadcaster== BroadcasterEnum.MOTOGP_OFFICIAL.value:
            #Case it's the official broadcaster
            sql = "SELECT PK_BROADCAST FROM BROADCAST WHERE GUID = %s "
            cursor.execute(sql, (broadcast.guid,))
            res = cursor.fetchone()
        elif broadcast.fk_broadcaster== BroadcasterEnum.TV8.value:
            #Case it's the TV8 broadcaster
            sql = """
                SELECT 
                    PK_BROADCAST 
                FROM 
                    BROADCAST 
                WHERE 
                    FK_BROADCASTER = %s 
                    AND FK_EVENT = %s
                    AND (
                        NAME = %s
                        OR START_DATE = CAST(%s AS DATETIME)
                    )
            """
            cursor.execute(sql, (
                BroadcasterEnum.TV8.value,
                broadcast.fk_event,
                broadcast.name,
                broadcast.start_date.isoformat()
            ))
            res = cursor.fetchone()
            
        broadcast_exists = res is not None
        if broadcast_exists:
            #UPDATE DATA (even if it's not changed)
            sql = """
                UPDATE BROADCAST
                SET
                    FK_EVENT = %s,
                    FK_CATEGORY = %s,
                    FK_KIND = %s,
                    NAME = %s,
                    START_DATE = %s,
                    END_DATE = %s,
                    DOU = CURRENT_TIMESTAMP
                WHERE
                    PK_BROADCAST = %s
            """
            cursor.execute(sql, (
                broadcast.fk_event, 
                broadcast.fk_category, 
                broadcast.fk_kind,
                broadcast.name, 
                broadcast.start_date.isoformat(), 
                broadcast.end_date.isoformat() if broadcast.end_date else None, 
                res[0]
            ))
            return res[0]
        else:
            #If it doesn't exists insert
            sql = """
                INSERT INTO BROADCAST
                    (FK_EVENT, FK_BROADCASTER, FK_CATEGORY, FK_KIND, GUID, NAME, IS_LIVE, START_DATE, END_DATE)
                VALUES
                    (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            cursor.execute(sql, (
                broadcast.fk_event, 
                broadcast.fk_broadcaster, 
                broadcast.fk_category, 
                broadcast.fk_kind, 
                broadcast.guid, 
                broadcast.name, 
                broadcast.is_live,
                broadcast.start_date.isoformat(), 
                broadcast.end_date.isoformat() if broadcast.end_date else None,
            ))
            return cursor.lastrowid