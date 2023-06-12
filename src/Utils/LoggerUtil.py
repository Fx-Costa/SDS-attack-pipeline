import logging
from Utils.ConfigUtil import ConfigUtil


class LoggerUtil:
    """

    """
    _instance = None
    _logger = None

    def __init__(self):
        raise RuntimeError("Must be instantiated using instance()")

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)

            # Create logging instance depending on verbose flag; root logger if set (includes library's' logs)
            # Otherwise a non-root logger; SDS-logger, which only logs from SDS-Attack-Pipeline.
            config = ConfigUtil.instance()
            logging.basicConfig(format=config["LOGGING"]["format"], datefmt=config["LOGGING"]["date_format"])
            if config["LOGGING"]["verbose"] == "False":
                cls._logger = logging.getLogger("SDS-logger")
                cls._logger.setLevel(config["LOGGING"]["level"])
            else:
                cls._logger = logging.getLogger()
                cls._logger.setLevel(config["LOGGING"]["level"])
        return cls._logger
