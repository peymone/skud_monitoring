from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from time import time


class APIChecker:
    """Class for check http response status"""

    def __init__(self) -> None:
        self.__api = dict()
        self.__api_status = dict()

        # Create api:desription dict by parsing api.txt
        with open(r'api_check\api.txt', 'r', encoding='utf-8') as file:
            for line in file.readlines():
                api = line.split()[0]
                description = ' '.join(line.split()[1:])
                self.__api[api] = description.strip()

    def http_request(self) -> dict:
        """Send http request for all servers and get http status codes"""

        # iterate over api list and check http status code
        for api_url, desc in self.__api.items():
            try:
                start_time = time()
                # send http request and get response
                with urlopen(api_url) as response:

                    # check open time
                    end_time = time()
                    open_time = f"{(end_time - start_time):0.3f}"

                    # Fill dictionary with result tuple
                    if response.status == 200:
                        self.__api_status[desc] = 'up', f"response time is {open_time} sec"
                    else:
                        self.__api_status[desc] = 'down', f"response time is {open_time} sec"

            # Error handlers
            except HTTPError as error:
                self.__api_status[desc] = 'down', error.reason
            except URLError as error:
                self.__api_status[desc] = 'down', error.reason
            except TimeoutError as error:
                self.__api_status[desc] = 'up', 'long delay'

        return self.__api_status


api_checker = APIChecker()
