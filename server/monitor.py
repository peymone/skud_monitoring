from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Event
from json import load
import socket

# Import application modules
from servers_check.checker import servers_checker
from api_check.checker import api_checker
from pretifier import rich
from logger import logger


class Server:
    def __init__(self, port) -> None:
        self.__host = socket.gethostbyname(socket.gethostname())
        self.__port = port
        self.__server_status = False
        self.__server_clients = dict()

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.__host, self.__port))

    def start(self):
        try:
            self.server_socket.listen()
            self.__server_status = True

            print('\n')
            rich.show(
                f"Server is running on {self.__host}:{self.__port}. Waiting for connections")
            logger.log.debug(
                f"Server is running on {self.__host}:{self.__port}. Waiting for connections")
            print('\n')

            while self.__server_status is True:
                client_socket, client_address = self.server_socket.accept()
                client_thread = Thread(target=self.__recieve_messages_fromClient, args=(
                    client_socket, client_address), daemon=True)
                client_thread.start()

        except OSError:
            pass

    def stop(self):
        if self.__server_status is False:
            pass
        else:
            pass

    def __recieve_messages_fromClient(self, cleint_socket, client_address):
        try:
            client_host = cleint_socket.recv(1024).decode('utf-8')
            self.__server_clients[client_host] = (
                cleint_socket, client_address)
            logger.log.debug(
                f"{client_address} esablished connection with name {client_host}")

            while client_host is self.__server_clients.keys():
                message = cleint_socket.recv(1024).decode('utf-8')
                match message:
                    case 'services_statuses':
                        services_statuses_json = cleint_socket.recv(
                            1024).decode('utf-8')
                        services_statuses = load(services_statuses_json)

                        lyrixServices_statusMsg = [
                            status[0] for status in services_statuses[0].values()]
                        ostelServices_statusMsg = [
                            status[0] for status in services_statuses[1].values()]

                        if ('Down' in lyrixServices_statusMsg) or ('pid not found' in lyrixServices_statusMsg):
                            rich.show(
                                f"Lyrix services status on {client_host}:", lvl='warning')
                            logger.log.warning(
                                f"Lyrix services status on {client_host}:")
                            print('\n')

                            for service_name, status in services_statuses[0].items():
                                if status[0] == 'Down':
                                    rich.show(
                                        f"{service_name.ljust(45)}{status[0].ljust(40)}last log was {status[1]}", lvl='error')
                                    logger.log.error(
                                        f"{service_name.ljust(45)}{status[0].ljust(40)}last log was {status[1]}")
                                elif status[0] == 'pid not found':
                                    rich.show(
                                        f"{service_name.ljust(45)}{status[0].ljust(40)}last log was {status[1]}", lvl='warning')
                                    logger.log.warning(
                                        f"{service_name.ljust(45)}{status[0].ljust(40)}last log was {status[1]}")
                        else:
                            rich.show(
                                f"{client_host.ljust(45)}All lyrix services is up", lvl='info')
                            logger.log.info(
                                f"{client_host.ljust(45)}All lyrix services is up")
                            print('\n')

                        if ('Down' in ostelServices_statusMsg) or ('Warning' in ostelServices_statusMsg):
                            rich.show(
                                f"Lyrix services status on {client_host}:", lvl='warning')
                            logger.log.warning(
                                f"Lyrix services status on {client_host}:")
                            print('\n')

                            for service_name, status in services_statuses[1].items():
                                if status[0] == 'Down':
                                    rich.show(
                                        f"{service_name.ljust(45)}{status[0].ljust(40)}last log was {status[1]}", lvl='critical')
                                    logger.log.critical(
                                        f"{service_name.ljust(45)}{status[0].ljust(40)}last log was {status[1]}")
                                elif status[0] == 'Warning':
                                    rich.show(
                                        f"{service_name.ljust(45)}{status[0].ljust(40)}last log was {status[1]}", lvl='warning')
                                    logger.log.warning(
                                        f"{service_name.ljust(45)}{status[0].ljust(40)}last log was {status[1]}")
                        else:
                            rich.show(
                                f"{client_host.ljust(45)}All ostel services is up", lvl='info')
                            logger.log.info(
                                f"{client_host.ljust(45)}All ostel services is up")
                            print('\n')

        except ConnectionResetError:
            logger.log.debug(
                f"{client_address} with name {client_host} disconnected")

            del self.__server_clients[client_host]

        except ConnectionAbortedError:
            pass


class Monitor:
    """Get and show data from checkers"""

    def __init__(self) -> None:
        self.__isActive = None
        self.__delay = None
        self.__event = Event()

    def start(self, delay: int = 15) -> None:
        """Get dada from checkers every n minutes"""

        if self.__isActive:  # Check if monitor is already working
            print('\n')
            rich.show("Monitor is already working", lvl='warning')
            print('\n')

        else:  # Start system monitoring
            self.__delay = delay * 60  # Convert minutes to seconds
            self.__isActive = True

            print('\n')
            rich.show(
                f"System monitoring has been started with {delay} minutes delay")
            logger.log.debug(
                f"System monitoring has been started with {delay} minutes delay")

            while self.__isActive:  # Start monitoring loop

                # Create a threads pool for get checkers data and parallel execution
                with ThreadPoolExecutor(2) as pull:

                    # Start threads
                    servers_status_thread = pull.submit(servers_checker.ping)
                    api_status_thread = pull.submit(api_checker.http_request)

                    # Create logs for starting threads
                    logger.log.debug("Checker threads has been started")

                    # getting results from threads
                    servers_status = servers_status_thread.result()
                    api_status = api_status_thread.result()

                    # Create log for ending threads
                    logger.log.debug("Checker threads has been ended")

                print('\n')
                rich.show("Servers status:\n")

                # Print results from servers_checker
                for server, status in servers_status.items():

                    if status[0] == 'down':  # Check if one of servers is down
                        rich.show(
                            f"{server.ljust(45)}{status[0].ljust(40)}{status[1]}", lvl='error')
                        logger.log.error(f"{server} is down - ping check")
                    elif 'up (package loss' in status[0]:  # Loss 1 - 99%
                        rich.show(
                            f"{server.ljust(45)}{status[0].ljust(40)}{status[1]}", lvl='warning')
                        logger.log.warning(
                            f"{server} is {status[0]} - ping check")
                    else:
                        rich.show(
                            f"{server.ljust(45)}{status[0].ljust(40)}{status[1]}", lvl='info')
                        logger.log.info(f"{server} is up - ping check")

                print('\n')
                rich.show("API's status:\n")

                # Pring results from api_checker
                for api, status in api_status.items():

                    if status[0] == 'down':  # Check if one of API's is down
                        rich.show(
                            f"{api.ljust(45)}{status[0].ljust(40)}{status[1]}", lvl='critical')
                        logger.log.critical(
                            f"{api} is down - http status check ({status[1]})")
                    else:
                        rich.show(
                            f"{api.ljust(45)}{status[0].ljust(40)}{status[1]}", lvl='info')
                        logger.log.info(
                            f"{api} is up - http status check ({status[1]})")

                # Show progress bar and wait for delay passing
                progressBar_thread = Thread(
                    target=rich.progress_bar, args=(self.__delay,), daemon=True)

                logger.log.debug("Progress bar thread has been started")
                progressBar_thread.start()  # Start progress bar thread

                # Wait for delay pass or event - loop can stop immediately
                self.__event.wait(self.__delay)

                progressBar_thread.join()  # Wait until progress bar end
                self.__event.clear()  # Set the event to False

            logger.log.debug("System monitoring has been stopped")

    def stop(self) -> None:
        """Stop system monitoring"""

        print('\n')

        if self.__isActive is True:
            self.__isActive = False
            self.__event.set()  # Set event to True - start loop can stop immediately
            rich.show("System monitoring has been stopped")
            logger.log.debug("System monitoring has been stopped")
        else:
            rich.show("Monitor is not working at the moment", lvl='warning')

        print('\n')

    def status(self) -> None:
        """Show system monitoring status"""

        print('\n')

        if self.__isActive:
            rich.show("Monitor is working")
        else:
            rich.show("Monitor is not working")

        print('\n')

    def show_delay(self) -> None:
        """Show system monitoring delay"""

        print('\n')

        if self.__isActive:
            rich.show(f"Monitor delay is {self.__delay//60} minutes")
        else:
            rich.show("Monitor is not working at the moment", lvl='warning')

        print('\n')

    def change_delay(self, delay: int) -> None:
        """Change delay for system monitoring"""

        print('\n')

        if self.__isActive:
            self.__delay = delay * 60  # Conver minutes to seconds
            self.__event.set()  # Set event to True - start loop can stop immediately

            rich.show(f"Monitor delay has been changed to {delay} minutes")
            logger.log.debug(
                f"Monitor delay has been changed to {delay} minutes")
        else:
            rich.show("Monitor is not working at the moment", lvl='warning')

        print('\n')

    def start_server(self, port):
        self.__server = Server(port)
        self.__server.start()

    def server_status(self):
        pass

    def server_clients(self):
        pass


monitor = Monitor()
