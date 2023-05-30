import os.path

from File.File import File
import pandas as pd
from Utils.LoggerUtil import LoggerUtil
from Utils.ConfigUtil import ConfigUtil

logger = LoggerUtil.instance()
config = ConfigUtil.instance()


class SyntheticDatasetFile(File):
    """
    SyntheticDatasetFile a concrete File class, allowing reading and writing to sensitive datasets (TSV files -
        handled as CSV files).
    """

    def __init__(self):
        """
        Initializes a SensitiveDatasetFile object using a TSV file extension.
        """
        path = config["GENERAL"]["root_dir"] + type(self).__name__.replace("File", "") + os.path.sep \
               + config["GENERAL"]["name"] + "_synthetic_microdata" + ".tsv"
        super().__init__(existing_path=path)

        # Save a reference to the original filename
        self.original_filename = self._filename

    def read(self, is_resynthesis=False):
        """
        Reads a SyntheticDatasetFile and returns its content as a pandas dataframe.

        :return: dataframe
        """
        # Read from the resynthezised synthetic dataset if is_resynthesis is set, by changing pointed to filename
        if is_resynthesis:
            self.change_file()

        # Check if the file exists
        self._exists()

        # Read the (resynthesized) synthetic dataset
        dataframe = pd.read_csv(self.path)

        logger.debug("Performed read on synthetic dataset; " + self.path)

        # Change back to the original filename if is_resynthesis is set
        if is_resynthesis:
            self.change_file(original=True)

        return dataframe

    def write(self, data):
        pass

    def change_file(self, original=False):
        """
        Modifies the internal file path to point to either the original or resynthesized synthetic dataset.

        :param original: boolean
        """
        if original:
            # Set the filename back to its original name
            self._set_filename(self.original_filename)
        else:
            # Adds '_resynthesis' to the filename prefix
            split = self.original_filename.split("_", 1)
            self._set_filename(split[0] + "_resynthesis" + "_" + split[1])
