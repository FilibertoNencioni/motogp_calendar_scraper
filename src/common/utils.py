import requests
from common.logger import LogType
from common.resource_factory import ResourceFactory


class Utils:
    @staticmethod
    def get_html_content(self, url):
        try:
            # Function to get HTML content from a URL
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            else:
                raise Exception(f"Failed to retrieve the webpage. Status code: {response.status_code}")

        except:
            msg = "An error occurred while retriving the HTML page\n"
            msg += f"\t\turl: {url}"

            ResourceFactory.logger.log(msg, LogType.ERROR)
            raise