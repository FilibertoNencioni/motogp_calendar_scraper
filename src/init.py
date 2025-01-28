from common.db_utils import DbUtils
from common.logger import LogType
from common.resource_factory import ResourceFactory
from services.tv8_service import Tv8Service
from services.motogp_service import MotoGpService
from dotenv import load_dotenv
from collections.abc import Callable

def main():
    #Initialize .env file
    load_dotenv()

    ResourceFactory.get_logger().log("STARTED")
    try:
        MotoGpService.execute()

        connection = ResourceFactory.get_db_connection()
        cursor = connection.cursor(buffered=True)
        has_data_for_season = DbUtils.check_if_has_official_data_for_season(cursor)
        cursor.close()
        
        if has_data_for_season:
            execute_service(Tv8Service.execute, "TV8 Service")
            
        else:
            ResourceFactory.get_logger().log("No official events available for this season. Skip parsing...", LogType.WARN)


        #MANAGE DELETE LOGS
        ResourceFactory.get_logger().clear_logs()
        ResourceFactory.get_logger().log("The program ended successfully!", LogType.INFO)
    except:
        ResourceFactory.get_logger().log_exception("General exception")


def execute_service(exec_func: Callable, service_name: str):
    try:
        exec_func()
    except:
        ResourceFactory.get_logger().log_exception(f"Error executing {service_name}")


if __name__ == "__main__":
    main()