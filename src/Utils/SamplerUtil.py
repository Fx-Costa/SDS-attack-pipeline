import pandas as pd
from Utils.ConfigUtil import ConfigUtil
from Utils.LoggerUtil import LoggerUtil

logger = LoggerUtil.instance()


class SamplerUtil:
    """
    A class for sampling a dataset using pandas dataframes.

    Methods: sample(), insert_sample(), insert_samples()
    """
    def __init__(self):
        """
        Creates an instance of SamplerUtil
        """
        self.dataset_path = ConfigUtil.instance()["SENSITIVE"]["dataset_path"]

    def sample(self, n=1, m=-1, cols=None):
        """
        Samples the dataset given by dataset_path n times

        :param n: the number of samples (int) defaults to 1
        :param m: the number of columns in samples (int) defaults to all
        :param cols: the specific columns in samples (a list of strings) defaults to none
        :return: an n by m, or n by cols (if given cols) sized pandas dataframe
        """
        # If m and cols are both given
        # the number of columns in cols must match m
        if m != -1 and cols is not None and m != len(cols):
            logger.error("Unsuccessful sampling; m = " + str(m) + " must match number of columns in cols = " + str(cols))
            return

        # Full dataframe
        dataframe = pd.read_csv(self.dataset_path, na_values='N')
        dataframe.index.name = "ID"

        # Dropping columns based on m and/or cols
        if m > 0 and cols is None:    # If only m is given
            # Drop all columns not in [0, m]
            dataframe = dataframe.drop(dataframe.iloc[:, m:len(dataframe.columns)], axis=1)
        elif cols is not None:    # If cols is given
            try:
                dataframe = dataframe[cols]
            except KeyError:
                logger.warning("Invalid input; cols = " + str(cols) + " do not exist in dataset, using all columns")

        # If n is non-positive; return the empty df
        if n < 1:
            logger.debug("Empty sampling; n = " + str(n) + " returning an empty df")
            return dataframe

        logger.debug("Successful sampling; created n = " + str(n) + " by m = " + str(m) +
                     " sized sample, using columns: " + str(list(dataframe.columns)))
        # return the n random samples
        return dataframe.sample(n)
