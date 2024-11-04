from typing import List
from mysql.connector.abstracts import MySQLCursorAbstract
from common.resource_factory import ResourceFactory
from common.logger import LogType
from common.enum.broadcaster_enum import BroadcasterEnum
from models.circuit import Circuit
from models.event import Event
from models.category import Category
from models.broadcast import Broadcast
import datetime
import json

class DbUtils:

##GENERAL
    @staticmethod
    def check_if_has_official_data_for_season(cursor: MySQLCursorAbstract)->bool:
        try:
            current_year = datetime.datetime.now().year
            sql = """
                SELECT COUNT(*) FROM EVENT
                WHERE SEASON = %s
            """
            cursor.execute(sql, (current_year,))
            res = cursor.fetchone()[0]
            return res > 0

        except:
            msg = "Error while checking if the DB has official data for the current season\n"
            msg += f"\t\tcurrent_year: {current_year}"
            ResourceFactory.get_logger().log(msg, LogType.ERROR)

##CIRCUIT
    @staticmethod
    def check_circuit(cursor: MySQLCursorAbstract, circuit: Circuit) -> int:
        try:
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

        except:
            msg = "Error while checking if a circuit already exists in the DB and updating/inserting it\n"
            msg += f"\t\tcircuit: {json.dumps(vars(circuit), default=str)}"
            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise
        
##EVENT
    @staticmethod
    def check_event(cursor: MySQLCursorAbstract, event: Event) -> int:
        try:
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

        except:
            msg = "Error while checking if a event already exists and updating/inserting it in the DB\n"
            msg += f"\t\tevent: {json.dumps(vars(event), default=str)}"
            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise
    
    @staticmethod
    def get_event_by_date(cursor: MySQLCursorAbstract, date: str) -> Event | None:
        try:
            sql = """
                SELECT
                    *
                FROM
                    EVENT
                WHERE
                    %s >= START_DATE
                    AND %s <= END_DATE 
            """

            cursor.execute(sql, (date, date))
            return Event(*cursor.fetchone())
        except:
            msg = "Error while getting an event by date from the DB\n"
            msg += f"\t\tdate: {date}"
            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise

##CATEGORY
    @staticmethod
    def get_all_categories(cursor: MySQLCursorAbstract) -> List[Category]:
        try:
            sql = "SELECT * FROM CATEGORY"
            cursor.execute(sql)
            return [Category(*row) for row in cursor.fetchall()]

        except:
            msg = "Error while getting all categories from the DB"
            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise
        
##BROADCAST
    @staticmethod
    def check_broadcast(cursor: MySQLCursorAbstract, broadcast: Broadcast) -> int:
        try:
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
                        (FK_EVENT, FK_BROADCASTER, FK_CATEGORY, GUID, NAME, IS_LIVE, START_DATE, END_DATE)
                    VALUES
                        (%s,%s,%s,%s,%s,%s,%s,%s)
                """

                cursor.execute(sql, (
                    broadcast.fk_event, 
                    broadcast.fk_broadcaster, 
                    broadcast.fk_category, 
                    broadcast.guid, 
                    broadcast.name, 
                    broadcast.is_live,
                    broadcast.start_date.isoformat(), 
                    broadcast.end_date.isoformat() if broadcast.end_date else None,
                ))
                return cursor.lastrowid

        except:
            msg = "Error while checking if a broadcast already exists and updating/inserting it in the DB\n"
            msg += f"\t\tbroadcast: {json.dumps(vars(broadcast), default=str)}"
            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise