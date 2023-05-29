import numpy as np
import pandas as pd
from Utils.LoggerUtil import LoggerUtil
from Utils.ConfigUtil import ConfigUtil

logger = LoggerUtil.instance()


class SyntheticAnalyser:

    def __init__(self):
        """
        Creates an instance of SyntheticAnalyser
        """
        self.config = ConfigUtil.instance()
        self.initial_syn_path = self.config["SYNTHETIC"]["dataset_dir"] + self.config["GENERAL"]["name"] \
            + "_synthetic_microdata.tsv"
        self.syn_path = self.config["SYNTHETIC"]["dataset_dir"] + self.config["GENERAL"]["name"] + "_resynthesis" \
            + "_synthetic_microdata.tsv"
        self.initial_syn_dataset = pd.read_csv(self.initial_syn_path)
        self.syn_dataset = pd.read_csv(self.syn_path)

    def determine_leak(self, payload):
        # Get the row of data from the payload dataframe
        payload_data = payload.iloc[0]

        # Check if the full row exists in the synthetic dataset
        row_exists = self.syn_dataset.apply(lambda row: row.equals(payload_data), axis=1).any()

        return row_exists
