import logging
from colorama import init, Fore, Style


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)
    
    
def get_logger():
    init(autoreset=True)
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = ColoredFormatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger
