import json
import logging
import os

# TODO: get root dir and supply to paths. See: syn_config_path, sensitive_csv_path (should be generalized) and
#  create_directory()
# TODO: Logging


def create_directory(directory):
    """
    Creates a directory at project root if the directory does not already exist. Necessary for below methods
    to run as intended if no required directories exist.

    :param directory: the name of the directory to create if it does not already exist
    :return: void
    """
    if not os.path.exists("../" + directory):
        os.makedirs("../" + directory)


class ConversionUtil:
    """
    A class for utility functions to perform on pandas datatables.

    Methods: dataframe_to_csv(), dataframe_to_syn_config()
    """

    def __init__(self, dataframe):
        """
        Creates an instance of ConversionUtils given a pandas dataframe

        :param dataframe: a pandas dataframe
        """
        self.dataframe = dataframe

        self.sensitive_csv_path = "C:\\Users\\Fx\\Desktop\\Bachelor Project\\SDS-attack-pipeline\\samples\\"
        self.sensitive_csv_identifier = None

        self.syn_config_path = "C:\\Users\\Fx\\Desktop\\Bachelor Project\\SDS-attack-pipeline\\configs\\"
        self.syn_config = {
            "sensitive_microdata_path": "",
            "sensitive_microdata_delimiter": ",",
            "use_columns": [],
            "record_limit": -1,
            "sensitive_zeros": [],
            "reporting_resolution": 1,
            "reporting_length": 3,
            "synthesis_mode": "value_seeded",
            "oversampling_ratio": 0.1,
            "oversampling_tries": 10,
            "parallel_jobs": 4,
            "cache_max_size": 10000,
            "output_dir": "../synthetic",
            "prefix": "",
            "report_title": "",
            "report_visuals": {},
            "report_pages": {}
        }

    def dataframe_to_csv(self, sensitive_csv_identifier):
        """
        Creates, in the 'samples' directory, a csv file from a dataframe with the given name sensitive_csv_identifier

        :param sensitive_csv_identifier: the name (identifier) of the sensitive csv formatted dataset
        :return: path to the created CSV file (string)
        """
        create_directory("samples")

        # Create CSV file
        self.sensitive_csv_identifier = sensitive_csv_identifier
        self.sensitive_csv_path = self.sensitive_csv_path + self.sensitive_csv_identifier + ".csv"
        self.dataframe.to_csv(self.sensitive_csv_path)

        return self.sensitive_csv_path

    def dataframe_to_syn_config(self, synthesis_mode, k):
        """
        Creates, in the 'configs' directory, a synthesis configuration file used to create synthetic datasets.
        The synthesis configuration includes the sensitive dataset given by the field; sensitive_csv.

        :param synthesis_mode: mode of synthesis; row_seeded, unseeded, value_seeded, or aggregate_seeded (as a string)
        :param k: the number k, to use in k-anonymity (as an int)
        :return: path to the created JSON file (string)
        """
        create_directory("configs")
        self.syn_config_path = self.syn_config_path + self.sensitive_csv_identifier + ".json"

        # Set synthesis config fields
        self.syn_config["sensitive_microdata_path"] = self.sensitive_csv_path
        self.syn_config["sensitive_zeros"] = list(self.dataframe.columns.values)
        self.syn_config["reporting_resolution"] = k
        self.syn_config["synthesis_mode"] = synthesis_mode
        self.syn_config["prefix"] = self.sensitive_csv_identifier

        # Create JSON file
        json_dump = json.dumps(self.syn_config)
        json_file = open(self.syn_config_path, "w")
        json_file.write(json_dump)
        json_file.close()

        return self.syn_config_path
