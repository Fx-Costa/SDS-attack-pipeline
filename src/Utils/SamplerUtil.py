import pandas as pd
import logging

# TODO: Logging. Logging of incorrect usage, logging status in sampling, etc.


class SamplerUtil:
    """
    A class for sampling a dataset using pandas dataframes.

    Methods: sample()
    """

    def __init__(self, dataset_path):
        """
        Creates an instance of SamplerUtil

        :param dataset_path: filepath to the dataset to sample from
        """
        self.dataset_path = dataset_path

    def sample(self, n=1, m=-1, cols=None):
        """
        Samples the dataset given by dataset_path n times

        :param n: the number of samples (int) defaults to 1
        :param m: the number of columns in samples (int) defaults to all
        :param cols: the specific columns in samples (a list of strings) defaults to none
        :return: a n by m, or n by cols (if given cols) sized pandas dataframe
        """
        # If m and cols are both given
        # the number of columns in cols must match m
        if m != -1 and cols is not None and m != len(cols):
            return

        # Full dataframe
        dataframe = pd.read_csv(self.dataset_path)
        dataframe.index.name = "ID"

        # Dropping columns based on m and/or cols
        if m > 0 and cols is None:    # If only m is given
            # Drop all columns not in [0, m]
            dataframe = dataframe.drop(dataframe.iloc[:, m:len(dataframe.columns)], axis=1)
        elif cols is not None:    # If cols is given
            dataframe = dataframe[cols]

        # return the n random samples
        return dataframe.sample(n)
