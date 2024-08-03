from common.logger import LogType
from common.resource_factory import ResourceFactory
from services.tv8_service import Tv8Service
from services.motogp_service import MotoGpService
from dotenv import load_dotenv
import sys
import traceback

def main():
    #Initialize .env file
    load_dotenv()

    ResourceFactory.get_logger().log("STARTED")

    try:
        MotoGpService.execute()
        # Tv8Service.execute()

        #MANAGE DELETE LOGS
        ResourceFactory.get_logger().clear_logs()

        ResourceFactory.get_logger().log("The program ended successfully!", LogType.INFO)



    except Exception as e:
        # Get current system exception
        ex_type, ex_value, ex_traceback = sys.exc_info()

        # Extract unformatter stack traces as tuples
        trace_back = traceback.extract_tb(ex_traceback)

        # Format stacktrace
        stack_trace = list()

        for trace in trace_back:
            stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

        logger_msg = "The program ended unexpectedly.\n"
        logger_msg += f"\t\tException type: {ex_type}\n"
        logger_msg += f"\t\tException message: {ex_value}\n"
        logger_msg += f"\t\tStack Trace: {stack_trace}"

        ResourceFactory.get_logger().log(logger_msg, LogType.ERROR)







if __name__ == "__main__":
    main()