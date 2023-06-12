import json
from File.File import File
from Utils.LoggerUtil import LoggerUtil
from Utils.ConfigUtil import ConfigUtil
from File.SensitiveDatasetFile import SensitiveDatasetFile
from File.SyntheticDatasetFile import SyntheticDatasetFile

logger = LoggerUtil.instance()
config = ConfigUtil.instance()


class SynthesisConfigFile(File):
    """
    SynthesisConfigFile a concrete File class, allowing reading and writing to synthetic config files (JSON files).
    """

    def __init__(self, sensitive_dataset_file: SensitiveDatasetFile, synthetic_dataset_file: SyntheticDatasetFile):
        """
        Initializes a SensitiveDatasetFile object using a JSON file extension.
        """
        super().__init__(file_extension=".json")

        # A SensitiveDatasetFile object
        self.sensitive_dataset_file = sensitive_dataset_file

        # A SyntheticDatasetFile object
        self.synthetic_dataset_file = synthetic_dataset_file

        # Save a reference to the
        self.original_filename = self._filename

        # A template for the synthesis configurations
        self.config_template = {
            "sensitive_microdata_path": self.sensitive_dataset_file.path,
            "sensitive_microdata_delimiter": ",",
            "use_columns": list(self.sensitive_dataset_file.read().columns),
            "record_limit": -1,
            "sensitive_zeros": list(self.sensitive_dataset_file.read().columns.values),
            "reporting_resolution": 1,
            "reporting_length": 3,
            "synthesis_mode": "unseeded",
            "oversampling_ratio": 0.1,
            "oversampling_tries": 10,
            "parallel_jobs": 4,
            "cache_max_size": 10000,
            "output_dir": self.synthetic_dataset_file._directory,
            "prefix": config["GENERAL"]["name"],
            "report_title": "",
            "report_visuals": {},
            "report_pages": {}
        }

    def read(self, is_resynthesis=False):
        """
        Reads a JSON file and returns its content as a dictionary.

        :return: dictionary
        """
        # Change the read configuration for resynthesization purposes (changes prefix) if is_resynthesis is set
        if is_resynthesis:
            self.change_file()

        # Check if the file exists
        self._exists()

        # Open and read the file
        file = open(self.path, "r")
        data = json.load(file)
        file.close()

        logger.debug("Performed read on synthesis-config; " + self.path)

        # Change the configurations (prefix) back to the original synthetic dataset
        if is_resynthesis:
            self.change_file(original=True)

        return data

    def write(self, data: dict, is_resynthesis=False):
        """
        Writes a given dictionary onto an existing JSON file by overwriting existing data.

        :param data: dictionary
        """
        # Change the configuration for resynthesization purposes (changes prefix) if is_resynthesis is set
        if is_resynthesis:
            self.change_file()

        # Check if the file exists
        self._exists()

        # Modify the config_template
        for key, val in data.items():
            self.config_template[key] = val

        # Write the synthesis configurations to the file
        json_dump = json.dumps(self.config_template)
        file = open(self.path, "w")
        file.write(json_dump)
        file.close()

        logger.debug("Performed write on synthesis-config; " + self.path + ". Wrote " + str(len(data.keys()))
                     + " lines")

        # Change the configurations (prefix) back to the original synthetic dataset
        if is_resynthesis:
            self.change_file(original=True)

    def change_file(self, original=False):
        """
        Modifies the prefix in the synthesis configurations to point to either the original or resynthesized synthetic
            dataset.

        :param original: boolean
        """
        if original:
            # Set the prefix back to its original name
            self.config_template["prefix"] = self.original_filename
        else:
            # Adds '_resynthesis' to the original prefix
            self.config_template["prefix"] = self.original_filename + "_resynthesis"
