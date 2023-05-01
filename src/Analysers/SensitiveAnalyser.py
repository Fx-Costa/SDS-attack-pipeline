import pandas as pd
from Utils.LoggerUtil import LoggerUtil

# TODO: right now this analysis is not used for anything, results should be used in attacks
logger = LoggerUtil.instance()


class SensitiveAnalyser:
    """
    A class for analyzing a sensitive dataset. Capable of determining types and ranges of features.
    E.g. a feature SEX can be marked as an int64 but only use values 1/2 - which is more explanatory as a binary.
    Why we want to determine the types- and ranges of values for later use.

    Methods: determine_ftr_type(), determine_ftr_ranges(), analyse()
    """

    def __init__(self, dataframe):
        """
        Creates an instance of SensitiveAnalyser

        :param dataframe: a pandas dataframe
        """
        self.dataframe = dataframe

        # Features types
        self.conclusive = None
        self.inconclusive = None

    def determine_ftr_types(self, dataframe):
        """
        Determines datatypes of features, i.e. what types of values each entry takes on per column.
        Uses pandas functionality in addition to 'manual' analysis where inconclusive or too broad.
        Conclusively typed features are those whose dtypes are set more specific than 'object'.

        :return: pandas dataframe
        """
        # Determine in- and conclusively typed features
        self.conclusive = self.dataframe.select_dtypes(exclude=["object"])
        self.inconclusive = self.dataframe.select_dtypes(include=["object"])

        # TODO: further analysis here. conclusive types are sometimes mistaken.
        #  for instance MSP could be int64 rather than float64
        # TODO: How to handle inconclusive dtypes, such as PUMA. Do we need a parser ?

        # Construct the dataframe with conclusive type labels
        for col in self.conclusive.columns:
            # Set the value of the "type" row for the column to its data type
            dataframe.loc["type", col] = str(self.conclusive[col].dtype)

        return dataframe

    def determine_ftr_ranges(self, dataframe):
        """
        Determines ranges of feature values, i.e. what range of values each entry takes on per column.
        May change datatype label where the range can be narrowed down. E.g. in cases where features have a constant
        and/or binary range of values.

        :return: pandas dataframe
        """
        # Determine ranges of values of conclusively typed columns
        ranges = self.conclusive.agg(['min', 'max'])
        ranges.loc["diff"] = ranges.loc['max'] - ranges.loc['min']

        # Determine constant and binary columns
        constant_columns = ranges.columns[ranges.loc['diff'] == 0]
        binary_columns = ranges.columns[ranges.loc['diff'] == 1]

        # Construct the dataframe with type labels, min, max and average values per column
        dataframe.loc["type", constant_columns] = "constant"
        dataframe.loc["type", binary_columns] = "binary"
        ranges.loc["avg"] = ranges.mean(axis=0)

        return pd.concat([dataframe, ranges.drop("diff")])

    def analyse(self):
        """
        Performs all steps in analysis, including all above methods. Return results in a pandas dataframe.

        :return: pandas dataframe
        """
        # Construct a dataframe to hold the analysed info
        df = pd.DataFrame(columns=self.dataframe.columns)
        df.loc["type"] = pd.Series()

        # Fill entries of the dataframe using above methods
        df = self.determine_ftr_types(df)
        df = self.determine_ftr_ranges(df)

        logger.debug("Successful analysis; created dataframe")
        return df
