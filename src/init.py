from scraper_utils import ScraperUtils 

def main():
    base_url = 'https://www.tv8.it'
    url = base_url+'/sport/motogp/calendario'

    scraper = ScraperUtils()
    
    links = scraper.extract_gran_prix_links(url)

    for link in links:
        events = scraper.extract_dates_from_page(base_url+link['link'])
        link['events'] = events

    print(events)

        





if __name__ == "__main__":
    main()