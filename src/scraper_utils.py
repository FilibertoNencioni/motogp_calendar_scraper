import requests
import dateparser
from bs4 import BeautifulSoup
import re
from resource_factory import ResourceFactory
from logger import LogType

class ScraperUtils:
    time_pattern = re.compile(r'^\d{2}:\d{2}$')

    def __init__(self) -> None:
        pass

    def __get_html_content(self, url):
        try:
            # Function to get HTML content from a URL
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            else:
                raise Exception(f"Failed to retrieve the webpage. Status code: {response.status_code}")

        except Exception as e:
            msg = "An error occurred while retriving the HTML page\n"
            msg += f"\t\turl: {url}"

            ResourceFactory.logger.log(msg, LogType.ERROR)
            raise e

    def extract_gran_prix_links(self, url):
        try:  
            # Function to extract links
            html_content = self.__get_html_content(url)

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
        except Exception as e:
            msg = "An error occurred while trying to retrieve all the races calendar links\n"
            msg += f"\t\turl: {url}"

            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise e
    
    def extract_dates_from_page(self, url: str):
        try:
            html_content = self.__get_html_content(url)
            soup = BeautifulSoup(html_content, 'html.parser')

            #oggetto che contiene tutte le informazioni sul Gran prix
            race_obj = dict()

            #Recupero tutte le date a sx della pagina, che raggruppano le giornate dal gran premio del singolo paese
            elements = [element for element in soup.find_all() if self.__lambda_find_race_day(element.get_text())]      

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
                    search_element = [element for element in current_element.find_all() if self.__check_if_str_is_time(element.get_text())]

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
        except Exception as e:
            msg = "An error occurred while trying to exctract the events on a race calendar page\n"
            msg += f"\t\turl: {url}"

            ResourceFactory.get_logger().log(msg, LogType.ERROR)
            raise e

    def __check_if_str_is_time(self, text: str):
        if str is None or str == "":
            return False
        return self.time_pattern.match(text.strip())
        
    def __lambda_find_race_day(self, text:str):
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