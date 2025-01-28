from common.logger import LogType
from common.resource_factory import ResourceFactory
from common.db_utils import DbUtils
from common.enum.broadcaster_enum import BroadcasterEnum
from common.enum.category_enum import CategoryEnum
from common.utils import Utils
from models.broadcast import Broadcast
from models.event import Event
from urllib.robotparser import RobotFileParser
import datetime
import re
import dateparser
from bs4 import BeautifulSoup
import pytz

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
            rp = Tv8Service.__initialize_roboparser()

            #Parse the calendar where all the GP are scheduled
            url = f"{Tv8Service.base_url}/sport/motogp/calendario"

            #Check if I can parse those information
            if not rp.can_fetch(url=url, useragent="*"):
                ResourceFactory.get_logger().log("Cannot read the calendar shedules due to robots.txt", LogType.WARN)
                return
            
            #If I'm here I can scrape the information on that URL
            links = Tv8Service.__extract_gran_prix_links(url)
            for link in links:
                event_link = f"{Tv8Service.base_url}{link['link']}"
                
                #Check if I can parse this informations
                if not rp.can_fetch(url=event_link, useragent="*"):
                    msg = "Cannot read the event link due to robots.txt.\n"
                    msg += f"\t\turl: {event_link}"
                    ResourceFactory.get_logger().log(msg, LogType.WARN)
                    return
                
                #Scrape the dates from the link
                events = Tv8Service.__extract_dates_from_page(Tv8Service.base_url+link['link'])
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
                        timezone = pytz.timezone('Europe/Rome')

                        #This "event" corresponds to the broadcast event emitted by tv8
                        for event in dates['events'].keys():
                            #Add the broadcasts if exists otherwise update
                            time = event.split(":")
                            event_date = timezone.localize(date.replace(hour=int(time[0]), minute=int(time[1])))
                            event_name = dates['events'][event]

                            #Now I need to get in which category this broadcast belongs (ex. MotoGP or Moto2) 
                            category_pk: int | None = Tv8Service.__get_category_pk_from_title(event_name)

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

    def __get_category_pk_from_title(string: str) -> int | None:
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

    def __initialize_roboparser() -> RobotFileParser:
        #Initialize parser for robots.txt (what you as a robot can do according to tv8 policy)
        rp = RobotFileParser()

        #Read robots.txt file 
        rp.set_url(f"{Tv8Service.base_url}/robots.txt")
        rp.read()

        #Log Robots.txt last modified 
        robots_last_modified = datetime.datetime.fromtimestamp(rp.modified()) if rp.modified() != None else None
        ResourceFactory.get_logger().log(f"TV8 robots.txt last modified in: {robots_last_modified or "NOT SPECIFIED"}", LogType.INFO)
        return rp
    

#### SCRAPING SECTION
    time_pattern = re.compile(r'^\d{2}:\d{2}$')

    def __extract_gran_prix_links(url):
        try:  
            # Function to extract links
            html_content = Utils.get_html_content(url)

            soup = BeautifulSoup(html_content, 'html.parser')
            links = []

            # Find all elements containing a string that starts with "Gran Premio"
            elements = soup.find_all(string=lambda text: text and text.strip().startswith("Gran Premio"))

            for element in elements:
                gp_name = element.get_text()
                link = ""
                parent = element.parent

                # Find all 'a' tags within the parent element
                while parent is not None and link == "":
                    #controllo prima se il parent stesso è un'anchor e nel caso prendo l'href
                    #atrimenti guardo se tra i child c'è qualcosa
                    if parent.name == "a":
                        href = parent.get("href")
                        if(href.startswith('/sport/motogp/')):
                            link = href

                    else:
                        a_tags = parent.find_all('a')

                        if len(a_tags) > 0:
                            for a in a_tags:
                                href = a.get('href')
                                if(href.startswith('/sport/motogp/')):
                                    #caso: ho trovato il link corretto
                                    link = href
                
                    parent = parent.parent
                            
                #controllo se ho trovato il link e che non sia già stato censito
                if link != "" and not any(d['link'] == link for d in links) :
                    tmp = dict()
                    tmp['gp_name']=gp_name
                    tmp['link']=link
                    links.append(tmp)
            
            return links
        except:
            msg = "An error occurred while trying to retrieve all the races calendar links\n"
            msg += f"\t\turl: {url}"

            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise
    
    def __extract_dates_from_page(url: str):
        try:
            html_content = Utils.get_html_content(url)
            soup = BeautifulSoup(html_content, 'html.parser')

            #oggetto che contiene tutte le informazioni sul Gran prix
            race_obj = dict()

            #Recupero tutte le date a sx della pagina, che raggruppano le giornate dal gran premio del singolo paese
            elements = [element for element in soup.find_all() if Tv8Service.__lambda_find_race_day(element.get_text())]      

            #Per ogni data recupero se è in diretta o in differita
            #In più mi parso la data scritta in data ISO (yyyy-mm-dd)
            for race_day in elements:
                #estrapolo la data
                unformatted_race_date = race_day.get_text()
                formatted_date = dateparser.parse(unformatted_race_date, date_formats=['%A %d %B'], languages=['it'])

                #recupero se è in differita (default None)
                is_live = None

                #prima controllo se è nel div dopo
                next_sibling = race_day.next_sibling
                if next_sibling is not None:
                    live_status = next_sibling.find(string=lambda text: text and text.lower().startswith(('live', 'differita')))
                    if len(live_status) > 0:
                        is_live = live_status.get_text().lower().startswith('live')
                
                #nel caso in cui is_live == None allora non ha il next sibling o non ha trovato lo stato
                #scorro quindi sempre più in alto fino a trovare la stringa "LIVE SU TV8" o "DIFFERITA SU TV8"
                if is_live is None:
                    tmp_element = race_day.parent
                    
                    while tmp_element is not None or is_live is None:
                        live_status = soup.find_all(string=lambda text: text and text.lower().startswith(('live', 'differita')))
                        if len(live_status) > 0:
                            is_live = live_status.get_text().lower().startswith('live')

                        tmp_element = tmp_element.parent


                #Ora recupero le date e l'evento per ogni giornata
                #le recupero andando a controllare dall'elemento "race_day" andando sempre più in alto (fermandomi quando trovo almeno una corrispondenza)
                #e cercando un'elemento che contenga un testo di questo formato "xx:xx" (dove x è un numero) e che abbia come elemento successivo uno che abbia del testo
                race_dates = dict()
                current_element = race_day.parent
                while current_element is not None and len(race_dates) == 0:
                    search_element = [element for element in current_element.find_all() if Tv8Service.__check_if_str_is_time(element.get_text())]

                    if len(search_element) > 0:
                        #caso: ho trovato la lista degli orari e eventi della gara
                        for time_element in search_element:
                            time = time_element.get_text()
                            event = time_element.next_sibling.get_text()
                            race_dates[time] = event
                    
                    current_element = current_element.parent


                
                #una volta recuperata la data e se è live o meno allora salvo queste informazioni nell'oggetto di cui farò il return
                tmp_date = formatted_date.strftime("%Y-%m-%d")
                race_obj[tmp_date] = dict()
                race_obj[tmp_date]['is_live']=is_live
                race_obj[tmp_date]['date']=tmp_date
                race_obj[tmp_date]['events']=race_dates

            return race_obj
        except:
            msg = "An error occurred while trying to exctract the events on a race calendar page\n"
            msg += f"\t\turl: {url}"

            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise

    def __check_if_str_is_time(text: str):
        if str is None or str == "":
            return False
        return Tv8Service.time_pattern.match(text.strip())
        
    def __lambda_find_race_day(text:str):
        if text is None or text == "":
            return False
        
        lower_text = text.lower()
        if lower_text.startswith(('venerdi', 'venerdì', 'sabato', 'domenica')) == False:
            return False

        #Controllo se effettivamente il testo trovato segue il formato del calendario tv8 (es. Sabato 23 Marzo)
        #evito di controllare all'indice 0 in quanto so già uno dei giorni scritti sopra
        splitted_text = lower_text.split(' ')

        if(len(splitted_text) != 3):
            return
        
        #Controllo il giorno
        if splitted_text[1].isnumeric() != True:
            return False
        
        months = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
        if splitted_text[2] in months:
            return True
        return False