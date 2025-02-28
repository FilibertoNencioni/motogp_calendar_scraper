import requests

class Utils:
    @staticmethod
    def get_html_content(url):
        # Function to get HTML content from a URL
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Failed to retrieve the webpage. Status code: {response.status_code}")
