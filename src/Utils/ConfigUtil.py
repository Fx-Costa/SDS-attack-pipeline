import configparser


class ConfigUtil:
    """

    """
    _instance = None
    _config = None

    def __init__(self):
        raise RuntimeError("Must be instantiated using instance()")

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._config = configparser.ConfigParser(interpolation=None)
            cls._config.read("Config.ini")
        return cls._config
