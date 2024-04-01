import os
import sys
import logging
import logging.handlers
from customexceptions import LoggerError


class Logger(logging.Logger):
    def __init__(self, name: str, filename: str = "", level: int = logging.DEBUG, stdout: bool = False) -> None:
        super().__init__(name, level)
        if not filename and not stdout:
            raise LoggerError(f"{self.__class__.__name__}: filename or stdout must be set.")
        if filename:
            self.pid = os.getpid()
            file_handler = logging.handlers.RotatingFileHandler(filename, maxBytes=1024*1024*32, backupCount=5)
            date_format = "%Y-%m-%d %H:%M:%S"
            formatter = logging.Formatter("[{asctime}] [{levelname:<8}] [{name}:%s]: {message}" % self.pid, datefmt=date_format, style="{")
            file_handler.setFormatter(formatter)
            self.addHandler(file_handler)
        if stdout:
            stdout_handler = logging.StreamHandler(sys.stdout)
            # stdout_handler.setLevel(logging.DEBUG)
            stdout_handler.setFormatter(formatter)
            self.addHandler(stdout_handler)


if __name__ == "__main__":
    log = Logger('test')