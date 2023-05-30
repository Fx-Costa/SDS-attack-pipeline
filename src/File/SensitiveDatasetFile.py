from File.File import File
import pandas as pd
from Utils.LoggerUtil import LoggerUtil
from Utils.ConfigUtil import ConfigUtil
from os.path import splitext, basename, dirname, isfile, sep
from typing import List

logger = LoggerUtil.instance()
config = ConfigUtil.instance()


class SensitiveDatasetFile(File):
    """
    SensitiveDatasetFile a concrete File class, allowing reading and writing to sensitive datasets (CSV files).
    """

    def __init__(self):
        """
        Initializes a SensitiveDatasetFile object using a CSV file extension.
        """
        super().__init__(file_extension=".csv")
        self.__dataset_path = config["SENSITIVE"]["dataset_path"]

    def read(self):
        """
        Reads a CSV and returns its content as a pandas dataframe.

        :return: dataframe
        """
        # Check if the file exists
        self._exists()

        dataframe = pd.read_csv(self.path)

        logger.debug("Performed read on sample; " + self.path)
        return dataframe.drop("ID", axis=1)

    def write(self, dataframe: pd.DataFrame, include_header=True):
        """
        Writes a given dataframe onto an existing CSV by appending to it.

        :param include_header: boolean
        :param dataframe: pandas dataframe
        """
        # Check if the sample exists
        self._exists()

        # Write the dataframe to the file
        dataframe.to_csv(self.path, mode='a', header=include_header)

        logger.debug("Performed write on sample; " + self.path + ". Appended " +
                     str(dataframe.shape[0]) + " rows")

    def change_file(self):
        pass
