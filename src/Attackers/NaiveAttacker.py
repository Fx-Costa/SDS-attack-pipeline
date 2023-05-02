import numpy as np
import pandas as pd
from Utils.SamplerUtil import SamplerUtil
from Utils.ConversionUtil import ConversionUtil
from Utils.ConfigUtil import ConfigUtil
from Utils.LoggerUtil import LoggerUtil

logger = LoggerUtil.instance()


class NaiveAttacker:
    """
    A class for naive attacks on a SDS synthesized dataset

    Methods: inject(), find_k(), leak()
    """

    def __init__(self, sensitive_analysis_df, synthesizer):
        """
        Creates an instance of NaiveAttacker

        :param cols: a list of column names (strings)
        :param synthesizer: a synthesizer object
        """
        self.sensitive_analysis_df = sensitive_analysis_df
        self.cols = self.sensitive_analysis_df.columns
        self.synthesizer = synthesizer
        self.config = ConfigUtil.instance()
        self.syn_csv_path = self.config["SYNTHETIC"]["dataset_dir"] + self.config["GENERAL"]["name"] + \
                            "_synthetic_microdata.tsv"

    def inject(self, dataframe):
        """
        Injects a Pandas dataframe into the sensitive dataset (often a sample) by appending to it

        :param dataframe: a pandas dataframe to 'inject' (append) to the sensitive dataset
        :return: void
        """
        dataframe.to_csv(self.config["SENSITIVE"]["sample_dir"] + self.config["GENERAL"]["name"] + ".csv", mode='a',
                         header=False)
        logger.debug("Performed injection; Appended " + str(dataframe.shape[0]) + " rows to sensitive dataset")

    def find_k(self, upper_bound=10):
        """
        Finds K of a synthetic dataset.
        Assumes that re-synthesis is possible with identical config. i.e. the syn_config is known, without knowing k.
        Linearly attempts to synthesize a sensitive dataset with k = 1 to upper_bound. When the synthetic dataset is
        non-empty we have found k (aggregate limit) used during the synthesis.

        :param upper_bound: the upper bound of k to try for
        :return: the integer k (aggregate limit) or void if unable to determine it within upper_bound
        """
        logger.info("Commencing attack; Finding K...")

        for k in range(1, upper_bound):
            k_sized_sample = SamplerUtil().sample(n=k, cols=self.cols)
            ConversionUtil(k_sized_sample).dataframe_to_csv()
            self.synthesizer.resynthesize()
            synthetic_df = pd.read_csv(self.syn_csv_path)

            if not synthetic_df.empty:
                logger.info("Successful attack; found k = " + str(k))
                return k

        logger.info("Unsuccessful attack; could not determine k within 1 to " + str(upper_bound))
        return

    def leak(self, k, target_column):
        print(self.sensitive_analysis_df)

        # Get sensitive dataset properties used to later determine injections
        type = self.sensitive_analysis_df[target_column]["type"]

        # Construct k injections (rows)
        #TODO: determine appropriate values to inject
        row = np.array([0, 0, 0, 0])
        injection = np.tile(row, (k, 1))

        # Create injection index labels; i0, i1, ..., ik
        index = ['i{}'.format(i) for i in range(k)]

        # Perform injection into sensitive dataset
        self.inject(pd.DataFrame(injection, index=index, columns=self.sensitive_analysis_df.columns))

        # Perform resynthesization
