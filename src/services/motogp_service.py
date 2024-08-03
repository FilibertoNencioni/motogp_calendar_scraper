from common.resource_factory import ResourceFactory
from common.logger import LogType
from datetime import datetime
import requests

from parsers.motogp_parser import MotoGpParser

class MotoGpService:
    baseurl = "https://api.motogp.pulselive.com/motogp/v1/events"

    def execute():
        try:
            ResourceFactory.get_logger().log("Executing MotoGP service")

            current_year = datetime.now().year
            api_response = MotoGpService.make_request(current_year)

            for json_circuit in api_response:
                #parse the JSON circuit to a Circuit object
                circuit = MotoGpParser.parse_circuit(json_circuit)

                #Check if it exists in the database
                



            ResourceFactory.get_logger().log("MotoGP service ended successfully")
        except Exception as e:
            ResourceFactory.get_logger().log("Error retrieving MotoGP data", LogType.ERROR)
            raise e
        

    def make_request(year: int):
        try:
            url = f"{MotoGpService.baseurl}?seasonYear={year}"

            response = requests.get(url)
            if response.status_code != 200:
                msg = "HTTP request failed\n"
                msg += f"\t\turl: {url}\n"
                msg += f"\t\tstatus code: {response.status_code}\n"
                msg += f"\t\treason phrase: {response.reason}"
                raise Exception(msg)
            
            #Once I've the response i return it decoded
            return response.json()
        except Exception as e:
            msg = "An unexpected error occurred while calling the MotoGP API\n"
            msg += f"\t\tyear: {year}"
            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise e
        

    