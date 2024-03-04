from concurrent.futures import ThreadPoolExecutor

from servicesChecker import services_checker
from .client import client


class Model:
    """Class for getting data from checkers and return values"""

    def __init__(self) -> None:
        pass

    def get_servicesStatuses(self) -> tuple[dict[str, tuple[str]], dict[str, tuple[str]] | str]:
        """Get data services statuses from Lyrix and ostel checkers"""

        # Thread pool for parallel checkers execution
        with ThreadPoolExecutor(2) as pool:
            lyrixChecker_thread = pool.submit(
                services_checker.get_lyrixServices_status)
            ostelChecker_thread = pool.submit(
                services_checker.get_ostelServices_status)

            # Get results from threads
            lyrixServices_status = lyrixChecker_thread.result()
            ostelServices_status = ostelChecker_thread.result()

        return lyrixServices_status, ostelServices_status

    def start_client(self, server_hostName, server_portNumber):
        client.start(server_hostName, server_portNumber)


model = Model()
