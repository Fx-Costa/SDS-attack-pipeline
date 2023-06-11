from abc import ABC, abstractmethod
from src.Utils.LoggerUtil import LoggerUtil
from src.Utils.ConfigUtil import ConfigUtil
from src.File.File import File

logger = LoggerUtil.instance()
config = ConfigUtil.instance()


class Analyzer(ABC):
    """
    An abstract class for Analyzer-like objects.
    """

    def __init__(self, file: File):
        """
        Initializes an Analyzer object using a File.
        """
        self.__file = file

    @property
    def _get_file(self):
        """
        Getter for file.

        :return: file
        """
        return self.__file

    @abstractmethod
    def analyze(self, data):
        raise NotImplementedError
