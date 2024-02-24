from os import popen  # use for run cmd command


class ServersChecker:
    """Class for check servers status by cmd ping command"""

    def __init__(self) -> None:
        self.__servers = dict()
        self.__ping_result = dict()
        self.__ping_errors = [
            'Destination host unreachable',
            'Request timed out',
            'Ping request could not find host',
            'При проверке связи не удалось обнаружить узел',
            'Превышен интервал ожидания для запроса']

        # Create server:desription dict by parsing servers.txt
        with open(r'servers_check\servers.txt', 'r', encoding='utf-8') as file:
            for line in file.readlines():
                server, description = line.split(':')
                self.__servers[server] = description.strip()

    def ping(self) -> dict:
        """Ping all servers and check for errors"""

        # Iterate over server dict and run cmd ping command
        for server, description in self.__servers.items():
            ping_res = popen('ping ' + server).read()  # ping server
            ping_res = ping_res.encode('cp1251').decode('cp866')  # Russian cmd
            error_ocured = False

            # Iterate over well known ping errors and check if they ocured in ping res
            for error in self.__ping_errors:
                if error in ping_res:
                    error_ocured = True
                    break

            # Fill dictionary with result tuple
            if error_ocured:
                self.__ping_result[server] = 'down', description
            else:
                self.__ping_result[server] = 'up', description

        return self.__ping_result


servers_checker = ServersChecker()
