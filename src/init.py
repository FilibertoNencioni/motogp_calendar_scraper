from logger import LogType
from resource_factory import ResourceFactory
from scraper_utils import ScraperUtils
from db_utils import DbUtils
from dotenv import load_dotenv
import sys
import traceback
import datetime
import urllib.robotparser


def main():
    #Initialize .env file
    load_dotenv()

    #Initialize parser for robots.txt (what you as a robot can do according to tv8 policy)
    rp = urllib.robotparser.RobotFileParser()

    ResourceFactory.get_logger().log("STARTED")

    try:
        base_url = 'https://www.tv8.it'

        #Read robots.txt file 
        rp.set_url(f"{base_url}/robots.txt")
        rp.read()

        #Log Robots.txt last modified 
        robots_last_modified = datetime.datetime.fromtimestamp(rp.modified()) if rp.modified() != None else None
        ResourceFactory.get_logger().log(f"TV8 ROBOTS LAST MODIFIED IN {robots_last_modified or "NOT SPECIFIED"}", LogType.INFO)

        #Parse the calendar where all the GP are scheduled
        url = f"{base_url}/sport/motogp/calendario"
        scraper = ScraperUtils()

        #Check if I can parse those information
        if not rp.can_fetch(url=url, useragent="*"):
            ResourceFactory.get_logger().log("Cannot read the calendar shedules due to robots.txt", LogType.WARN)
            return
        
        #If I'm here I can scrape the information on that URL
        links = scraper.extract_gran_prix_links(url)
        for link in links:
            event_link = f"{base_url}{link['link']}"
            
            #Check if I can parse this informations
            if not rp.can_fetch(url=event_link, useragent="*"):
                msg = "Cannot read the event link due to robots.txt.\n"
                msg += f"\t\turl: {event_link}"
                ResourceFactory.get_logger().log(msg, LogType.WARN)
                return
            
            #Scrape the dates from the link
            events = scraper.extract_dates_from_page(base_url+link['link'])
            link['events'] = events

        #Una volta estratti gli eventi e le date le salvo sul DB
        #DB TYPE sqlite
        connection = ResourceFactory.get_db_connection()
        cursor = connection.cursor()

        try:
            #Controllo se esistono le 2 tabelle che si utilizzano (GRAND_PRIX e EVENTS)
            DbUtils.check_tables(cursor)

            for link in links:
                gp_exists = DbUtils.check_if_has_grand_prix_this_year(cursor, link['gp_name'])
                gp_pk = DbUtils.get_pk_gp_from_name_this_year(cursor, link['gp_name']) if gp_exists else DbUtils.insert_gp(cursor, link['gp_name'])

                for dates in link['events'].values():
                    is_live = dates["is_live"]
                    date = datetime.datetime.strptime(dates['date'], '%Y-%m-%d')

                    for event in dates['events'].keys():
                        #Aggiungo (se esiste) l'evento
                        time = event.split(":")
                        event_date = date.replace(hour=int(time[0]), minute=int(time[1]))
                        event_name = dates['events'][event]
                        DbUtils.add_event_for_gp_if_not_exists(cursor, gp_pk, event_name, event_date, is_live)

                connection.commit()

        except Exception as db_ex:
            connection.rollback()
            raise db_ex
        
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