from os import popen  # use for run cmd command
import re  # use for check package loss


class ServersChecker:
    """Class for check servers status by cmd ping command"""

    def __init__(self) -> None:
        self.__servers = dict()
        self.__ping_result = dict()
        self.pingLoss_pattern = re.compile(r"\(\d+% \w+\)")

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

            # Search packacge loss count in ping result - match object
            ping_loss = self.pingLoss_pattern.search(ping_res)

            if ping_loss is not None:  # Match object in ping result
                # Convert match object to integer
                loss_count = int(ping_loss.group().split()[0][1:-1])

                if loss_count == 0:  # 0% package loss
                    self.__ping_result[server] = 'up', description
                elif loss_count == 100:  # 100% package loss
                    self.__ping_result[server] = 'down', description
                else:  # 1 - 99% package loss
                    self.__ping_result[server] = f'up (package loss {
                        loss_count}%)', description

            # No match object in ping result - None
            else:
                self.__ping_result[server] = 'down', description

        return self.__ping_result


servers_checker = ServersChecker()
