from threading import Thread

from monitor import monitor
from pretifier import rich
from logger import logger


class Console:
    def __init__(self) -> None:
        self.__command = None
        self.__commands = {
            'exit': "Close the admin_console",
            'commands': "Show all available commands",

            'start |minutes|': "Start system monitoring every n minutes (15 by default)",
            'stop': "Stop system monitoring",
            'status': "Show current monitor status",
            'delay': "Show system monitoring delay",
            'delay |minutes|': "Change system monitoring delay to (minutes)",

            'server': "Show current server status",
            'clients': 'Show current connected clients',
        }

    def show_commands(self) -> None:
        """Show all available commands"""
        print('\n')

        for command, description in self.__commands.items():
            rich.show(f"{command.ljust(60)}{description}", lvl='commands')

        print('\n')

    def commands_handler(self) -> None:
        while self.__command != 'exit':
            try:
                # Enter commands until 'exit'
                self.__command = rich.enter("Enter command /> ", 'system')
                rich.progressBar_status = False

                # Check if command have more than 1 word
                if len(self.__command.split()) >= 2:
                    command_msg = self.__command.split()[0]
                    command_arg = self.__command.split()[1]
                else:
                    command_msg = self.__command
                    command_arg = None

                # Execute command
                match command_msg:
                    case 'commands': self.show_commands()
                    case 'start':
                        if command_arg is not None:
                            # Check if command arg is integer
                            try:
                                delay = int(command_arg)
                                monitor_thread = Thread(
                                    target=monitor.start, daemon=True, args=(delay,))
                                monitor_thread.start()

                            except ValueError:
                                print('\n')
                                rich.show(
                                    "Monitor delay has to be integer", lvl='warning')
                                print('\n')
                        # Command argument is empty
                        else:
                            monitor_thread = Thread(
                                target=monitor.start, daemon=True)
                            monitor_thread.start()
                    case 'stop': monitor.stop()
                    case 'status': monitor.status()
                    case 'delay':
                        if command_arg is not None:
                            # Check if command arg is integer
                            try:
                                delay = int(command_arg)
                                monitor.change_delay(delay)
                            except ValueError:
                                print('\n')
                                rich.show(
                                    "Monitor delay has to be integer", lvl='warning')
                                print('\n')
                        # Command argument is empty
                        else:
                            monitor.show_delay()
                    case 'server': monitor.server_status()
                    case 'clients': monitor.server_clients()

            except KeyboardInterrupt:
                self.__command = 'exit'

        logger.log.debug("Progamm was closed")
        print('\n')


if __name__ == '__main__':
    admin_console = Console()
    logger.log.debug("Proram was started")

    print('\n')
    rich.show("Available commands:", lvl='system')
    admin_console.show_commands()
    admin_console.commands_handler()
