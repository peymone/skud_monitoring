import logging


class Logger:
    def __init__(self) -> None:
        self.log = logging.getLogger('__logger__')
        self.log.setLevel(logging.DEBUG)

        # Create a file for logger handling
        handler = logging.FileHandler('logs.log', mode='a', encoding='utf-8')
        # Set a format for log message
        formatter = logging.Formatter(
            '%(asctime)s\t%(levelname)s\t%(message)s', '%d-%m-%Y %H:%M:%S')

        # Add formatter to handler
        handler.setFormatter(formatter)
        # Add handler to logger
        self.log.addHandler(handler)


logger = Logger()
