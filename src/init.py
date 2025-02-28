from datetime import datetime
from common.db_utils import DbUtils
from common.logger import LogType
from common.resource_factory import ResourceFactory
from services.tv8_service import Tv8Service
from services.motogp_service import MotoGpService
from dotenv import load_dotenv
from collections.abc import Callable
from dateutil.relativedelta import relativedelta

def main():
    #Initialize .env file
    load_dotenv()

    ResourceFactory.get_logger().log("STARTED")
    try:
        MotoGpService.execute()

        if can_scrape():
            execute_service(Tv8Service.execute, "TV8 Service")
            

        #MANAGE DELETE LOGS
        ResourceFactory.get_logger().clear_logs()
        ResourceFactory.get_logger().log("The program ended successfully!", LogType.INFO)
    except:
        ResourceFactory.get_logger().log_exception("General exception")



def can_scrape():
    """Determine if it's possible to scrape the unofficial broadcaster schedule"""
    connection = ResourceFactory.get_db_connection()
    cursor = connection.cursor(buffered=True)
    
    has_data_for_season = DbUtils.has_official_data_for_season(cursor)
    if(not has_data_for_season):
        ResourceFactory.get_logger().log("No official events available for this season. Skip parsing...", LogType.WARN)
        return False
    
    first_event_date = DbUtils.first_event_date_of_season(cursor)
    cursor.close()

    if((datetime.today() + relativedelta(months=1)).date() < first_event_date):
        ResourceFactory.get_logger().log("The scraping processes will start a month before the first official event scheduled date", LogType.WARN)
        return False
    return True


def execute_service(exec_func: Callable, service_name: str):
    try:
        exec_func()
    except:
        ResourceFactory.get_logger().log_exception(f"Error executing {service_name}")


if __name__ == "__main__":
    main()