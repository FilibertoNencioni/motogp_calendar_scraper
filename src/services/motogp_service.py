from typing import List
from common.resource_factory import ResourceFactory
from common.logger import LogType
from common.db_utils import DbUtils
from models.circuit import Circuit
from models.event import Event
from models.category import Category
from models.broadcast import Broadcast
from datetime import datetime
import requests

class MotoGpService:

    def execute():
        try:
            ResourceFactory.get_logger().log("Executing MotoGP service")

            current_year = datetime.now().year
            api_response = MotoGpService.make_request(current_year)

            connection = ResourceFactory.get_db_connection()
            cursor = connection.cursor()


            for json_circuit in api_response:
                if json_circuit["circuit"] is None:
                    continue

                #Then I check if the event has kind "GP", otherwise skip to the next event
                #becouse there won't be any event unnless it's a race event (TEST and others will be discarded)
                if json_circuit["kind"] != "GP":
                    continue

                #parse the JSON circuit to a Circuit object
                circuit = Circuit.from_motogp_service(json_circuit)
                #Check if it exists in the database
                pk_circuit = DbUtils.check_circuit(cursor, circuit)
                circuit.pk_circuit = pk_circuit

                #Now check the events of that circuit
                event = Event.from_motogp_service(json_circuit, circuit.pk_circuit)

                #Check if it exists in the database
                pk_event = DbUtils.check_event(cursor, event)
                event.pk_event = pk_event

                
                broadcast_cats:List[Category] = DbUtils.get_all_categories(cursor)
                json_broadcasts = json_circuit["broadcasts"]

                for json_broadcast in json_broadcasts:
                    #Check if the category of the broadcast exists in the database
                    #Only broadcasts with existing category can be saved
                    broadcast_category_id = json_broadcast["category"]["id"]
                    found_category: Category | None = next((x for x in broadcast_cats if x.guid == broadcast_category_id), None)
                    if found_category is None:
                        continue
                    
                    broadcast = Broadcast.from_motogp_service(json_broadcast, event.pk_event, found_category.pk_category)
                    DbUtils.check_broadcast(cursor, broadcast)
            
            #TODO: check if some circuit has been skipped (event dismissed)
            connection.commit()
            ResourceFactory.get_logger().log("MotoGP service ended successfully")
        except:
            connection.rollback()
            ResourceFactory.get_logger().log("Error retrieving MotoGP data", LogType.ERROR)
            raise
        

    def make_request(year: int):
        try:
            url = f"https://api.motogp.pulselive.com/motogp/v1/events?seasonYear={year}"

            response = requests.get(url)
            if response.status_code != 200:
                msg = "HTTP request failed\n"
                msg += f"\t\turl: {url}\n"
                msg += f"\t\tstatus code: {response.status_code}\n"
                msg += f"\t\treason phrase: {response.reason}"
                raise Exception(msg)
            
            #Once I've the response i return it decoded
            return response.json()
        except:
            msg = "An unexpected error occurred while calling the MotoGP API\n"
            msg += f"\t\tyear: {year}"
            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise 
        

    