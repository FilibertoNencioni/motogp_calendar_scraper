from common.logger import LogType
from common.resource_factory import ResourceFactory
from common.scraper_utils import ScraperUtils
from common.db_utils import DbUtils
from common.enum.broadcaster_enum import BroadcasterEnum
from common.enum.category_enum import CategoryEnum
from models.broadcast import Broadcast
from models.event import Event
from urllib.robotparser import RobotFileParser
import datetime

class Tv8Service:
    base_url = 'https://www.tv8.it'

    def execute():
        try:            
            ResourceFactory.get_logger().log("Executing TV8 service")

            connection = ResourceFactory.get_db_connection()
            cursor = connection.cursor(buffered=True)
            
            #Check if the official dates are in the DB so to know if the dates from TV8 website are updated for this season
            if not DbUtils.check_if_has_official_data_for_season(cursor):
                ResourceFactory.get_logger().log("No official Grand Prix dates available for this year. The process will end.\nTv8 service ended successfully", LogType.WARN)
                return

            #Initialize parser for robots.txt (what you as a robot can do according to tv8 policy)
            rp = Tv8Service.initialize_roboparser()

            #Parse the calendar where all the GP are scheduled
            url = f"{Tv8Service.base_url}/sport/motogp/calendario"
            scraper = ScraperUtils()

            #Check if I can parse those information
            if not rp.can_fetch(url=url, useragent="*"):
                ResourceFactory.get_logger().log("Cannot read the calendar shedules due to robots.txt", LogType.WARN)
                return
            
            #If I'm here I can scrape the information on that URL
            links = scraper.extract_gran_prix_links(url)
            for link in links:
                event_link = f"{Tv8Service.base_url}{link['link']}"
                
                #Check if I can parse this informations
                if not rp.can_fetch(url=event_link, useragent="*"):
                    msg = "Cannot read the event link due to robots.txt.\n"
                    msg += f"\t\turl: {event_link}"
                    ResourceFactory.get_logger().log(msg, LogType.WARN)
                    return
                
                #Scrape the dates from the link
                events = scraper.extract_dates_from_page(Tv8Service.base_url+link['link'])
                link['events'] = events

            #Once extracted all the events and dates those will be saved in the DB
            try:
                for link in links:
                    
                    for dates in link['events'].values():
                        #Check if I have this GP event in the database searching by date
                        #Skip this cycle if no event is found
                        off_event: Event | None = DbUtils.get_event_by_date(cursor, dates['date'])
                        if off_event is None:
                            continue

                        is_live = dates["is_live"]
                        date = datetime.datetime.strptime(dates['date'], '%Y-%m-%d')

                        #This "event" corresponds to the broadcast event emitted by tv8
                        for event in dates['events'].keys():
                            #Add the broadcasts if exists otherwise update
                            time = event.split(":")
                            event_date = date.replace(hour=int(time[0]), minute=int(time[1]))
                            event_name = dates['events'][event]

                            #Now I need to get in which category this broadcast belongs (ex. MotoGP or Moto2) 
                            category_pk: int | None = Tv8Service.get_category_pk_from_title(event_name)

                            broadcast = Broadcast(
                                0,
                                off_event.pk_event,
                                BroadcasterEnum.TV8.value,
                                category_pk,
                                None,
                                event_name,
                                is_live,
                                event_date,
                                None,
                                None,
                                None
                            )

                            #check if the broadcast is already in the DB (update/insert)
                            DbUtils.check_broadcast(cursor, broadcast)

                    connection.commit()
            except:
                connection.rollback()
                raise
            
            ResourceFactory.get_logger().log("Tv8 service ended successfully")
        
        except:
            ResourceFactory.get_logger().log("Error during the scraping of TV8 broadcast")
            raise

    def get_category_pk_from_title(string: str) -> int | None:
        string = string.lower()

        if "motogp" in string or "moto gp" in string:
            return CategoryEnum.MOTOGP.value
        elif "motoe" in string or "moto e" in string:
            return CategoryEnum.MOTOE.value
        elif "moto2" in string or "moto 2" in string:
            return CategoryEnum.MOTO2.value
        elif "moto3" in string or "moto 3" in string:
            return CategoryEnum.MOTO3.value
        else:
            return None

    def initialize_roboparser() -> RobotFileParser:
        #Initialize parser for robots.txt (what you as a robot can do according to tv8 policy)
        rp = RobotFileParser()

        #Read robots.txt file 
        rp.set_url(f"{Tv8Service.base_url}/robots.txt")
        rp.read()

        #Log Robots.txt last modified 
        robots_last_modified = datetime.datetime.fromtimestamp(rp.modified()) if rp.modified() != None else None
        ResourceFactory.get_logger().log(f"TV8 robots.txt last modified in: {robots_last_modified or "NOT SPECIFIED"}", LogType.INFO)
        return rp
    
    