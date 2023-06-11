import pandas as pd
from src.Utils.LoggerUtil import LoggerUtil
from src.Analyzers.Analyzer import Analyzer
from src.File.SensitiveDatasetFile import SensitiveDatasetFile

logger = LoggerUtil.instance()


class SensitiveAnalyzer(Analyzer):

    def __init__(self, sensitive_dataset_file: SensitiveDatasetFile):
        super().__init__(sensitive_dataset_file)

    def __determine_data_types(self, data: pd.DataFrame):
        """
        Determines data types of columns in the given sample.

        :param data: dataframe
        :return: dataframe
        """
        df = pd.DataFrame(columns=data.columns)

        # Iterate each column, inserting their datatype into the dataframe
        for col in data.columns:
            df.loc["type", col] = data[col].dtype

        return df

    def __determine_data_ranges(self, data: pd.DataFrame):
        """
        Determines minimum and maximum values for each column in the given sample, to describe the domain's range,
            and whether the NaN value should be considered in the domain's range.


        :param data: dataframe
        :return: dataframe
        """
        df = pd.DataFrame(columns=data.columns)

        # Get whether any column takes on NaN values
        df.loc["has_NaN"] = data.isna().any()

        # Get minimum and maximum values and insert them into the dataframe
        ranges = data.agg(["min", "max"])

        return pd.concat([df, ranges])

    def analyze(self, data: pd.DataFrame):
        """
        Performs analysis of the given sample on ranges of values and data types.

        :param data: dataframe
        :return: dataframe
        """
        df1 = self.__determine_data_types(data)
        df2 = self.__determine_data_ranges(data)
        return pd.concat([df1, df2])
