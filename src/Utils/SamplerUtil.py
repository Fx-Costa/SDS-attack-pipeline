import pandas as pd
from src.Utils.ConfigUtil import ConfigUtil
from src.Utils.LoggerUtil import LoggerUtil

logger = LoggerUtil.instance()
config = ConfigUtil.instance()


class SamplerUtil:
    """
    A class for sampling a dataset using pandas dataframes.

    Methods: sample(), insert_sample(), insert_samples()
    """
    def __init__(self):
        """
        Initializes an instance of SamplerUtil.
        """
        self.dataset_path = config["SENSITIVE"]["dataset_path"]

    def sample(self, n=1, m=-1, cols=None):
        """
        Creates CSV file given a pandas dataframe in the corresponding directory at root by overwriting.

        :param n: integer
        :param m: integer
        :param cols: list of strings
        """
        # If m and cols are both given the number of columns in cols must match m
        if m != -1 and cols is not None and m != len(cols):
            raise ValueError("m=" + str(m) + " must match the number of columns in cols=" + str(len(cols)))
        if n < 1 or not isinstance(n, int):
            raise ValueError("n=" + str(n) + " must be a positive integer")

        # Read the sensitive dataset
        sensitive_dataset = pd.read_csv(self.dataset_path, na_values='N')
        sensitive_dataset.index.name = "ID"

        # Drop columns not in within 0 to m, if cols is not given
        if m != -1 and cols is None:
            # Drop columns with indices not in [0, m]
            sensitive_dataset = sensitive_dataset.drop(
                sensitive_dataset.iloc[:, m:len(sensitive_dataset.columns)],
                axis=1
            )
        elif cols is not None:
            # Include only columns that appear in cols
            sensitive_dataset = sensitive_dataset[cols]

        logger.debug("Created sample; n = " + str(n) + " by m = " + str(m) + ", columns: " +
                     str(list(sensitive_dataset.columns)))
        return sensitive_dataset.sample(n)
