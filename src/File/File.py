import os
from abc import ABC, abstractmethod
from os.path import isfile, getsize
from os import makedirs
from Utils.LoggerUtil import LoggerUtil
from Utils.ConfigUtil import ConfigUtil

logger = LoggerUtil.instance()
config = ConfigUtil.instance()


class File(ABC):
    """
    An abstract class for File-like objects.
    """

    def __init__(self, file_extension: str = ".txt", existing_path: str = None):
        """
        Initializes a File-like object by creating a directory and file.
        """
        if existing_path is None:
            self.__directory = self.__create_directory()
            filename, extension = self.__create_file(file_extension)
            self.__filename = filename
            self.__extension = extension
        else:
            self.__parse_path(existing_path)

    @property
    def _directory(self):
        """
        A getter for the path of a File.

        :return: string
        """
        return self.__directory

    @property
    def _filename(self):
        """
        A getter for the filename of a File.

        :return: string
        """
        return self.__filename

    def _set_filename(self, filename: str):
        """
        A setter for the filename of a File.

        :param filename: string
        """
        self.__filename = filename

    @property
    def _extension(self):
        """
        A getter for the file extension of a File.

        :return: string
        """
        return self.__extension

    @property
    def path(self):
        """
        A getter for the full filepath.

        :return: string
        """
        return self.__directory + self.__filename + self.__extension

    @abstractmethod
    def read(self):
        raise NotImplementedError

    @abstractmethod
    def write(self, data):
        raise NotImplementedError

    @abstractmethod
    def change_file(self):
        raise NotImplementedError

    def _exists(self):
        """
        Checks if the file pointed to by path exists.
        Throws: FileNotFoundError, if the file given at initialization does not exist on the path or if empty.

        :return: boolean
        """
        filepath = self.path
        if not isfile(filepath):
            raise FileNotFoundError("The file does not exist: " + filepath)
        return True

    def __create_directory(self):
        """
        Creates a directory at the project root using the name of the File class, returns the path.

        :return: boolean
        """
        directory_name = type(self).__name__.replace("File", "")

        path = config["GENERAL"]["root_dir"]
        makedirs(path + directory_name, exist_ok=True)

        logger.debug("Created directory; " + path + directory_name)
        return path + directory_name + os.path.sep

    def __create_file(self, extension):
        """
        Creates a file at the directory pointed to by _directory.

        :return: boolean
        """
        filename = config["GENERAL"]["name"]

        open(self.__directory + filename + extension, 'w').close()

        logger.debug("Created file; " + self.__directory + filename + extension)
        return filename, extension

    def __parse_path(self, path):
        """
        Parses an existing filepath into a path, filename and extension.

        :param path: the existing filepath
        """
        # Split the path into a directory and a file
        path_split = path.rsplit(os.path.sep, 1)
        file_split = path_split[1].rsplit(".", 1)

        # Assign the parsed directory, filename and extension to fields
        self.__directory = path_split[0] + os.path.sep
        self.__filename = file_split[0]
        self.__extension = "." + file_split[1]
