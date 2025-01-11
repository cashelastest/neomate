import logging
import colorlog


class Logger:
    def create_logger(self):
        loger = logging.getLogger(__name__)
        if not loger.handlers:
            loger.setLevel(logging.INFO)
            formatter = colorlog.ColoredFormatter("%(log_color)s %(asctime)s %(levelname)s %(message)s",log_colors={
                        "DEBUG": "cyan",
                        "INFO": "bold_green",
                        "WARNING": "yellow",
                        "ERROR": "bold_red",
                        "CRITICAL": "bold_red",
                })
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            loger.addHandler(handler)
        loger.propagate = False
        return loger