import pandas as pd
from src.Utils.LoggerUtil import LoggerUtil
from src.Analyzers.Analyzer import Analyzer
from src.File.SyntheticDatasetFile import SyntheticDatasetFile

logger = LoggerUtil.instance()


class SyntheticAnalyzer(Analyzer):

    def __init__(self, synthetic_dataset_file: SyntheticDatasetFile):
        super().__init__(synthetic_dataset_file)

    def __determine_leak(self, payload_data: pd.Series):
        """
        Determines if the given payload resulted in a leak in the synthetic dataset.

        :param payload_data: series
        :return: boolean
        """
        # Read the synthetic dataset
        synthetic_dataset = self._get_file.read(is_resynthesis=True)

        # Check if the full row exists in the synthetic dataset
        exists = synthetic_dataset.apply(lambda row: row.equals(payload_data), axis=1).any()

        return exists

    def analyze(self, payload: pd.DataFrame):
        """
        Performs analysis on the synthetic dataset given a payload to determine if leaks has occurred.

        :param payload: dataframe
        :return: boolean
        """
        payload_data = payload.iloc[0]
        return self.__determine_leak(payload_data)
