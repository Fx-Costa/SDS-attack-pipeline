import pandas as pd
from Utils.SamplerUtil import SamplerUtil
from Utils.ConversionUtil import ConversionUtil
from Utils.ConfigUtil import ConfigUtil
import logging


class FindKAttack:
    """
    A class for determining K of a synthetic dataset.

    Methods: sample()
    """

    def __init__(self, cols, synthesizer):
        """
        Creates an instance of FindKAttack
        :param cols: a list of column names (strings)
        :param synthesizer: a synthesizer object
        """
        self.cols = cols
        self.synthesizer = synthesizer
        config = ConfigUtil.instance()
        self.syn_csv_path = config["SYNTHETIC"]["dataset_path"] + config["GENERAL"]["name"] + "_synthetic_microdata.tsv"

    def find_k(self, upper_bound=10):
        """
        Finds K of a synthetic dataset.
        Assumes that re-synthesis is possible with identical config.
        :return:
        """
        logging.info("Commencing attack; Finding K...")

        for k in range(1, upper_bound):
            k_sized_sample = SamplerUtil().sample(n=k, cols=self.cols)
            ConversionUtil(k_sized_sample).dataframe_to_csv()
            self.synthesizer.resynthesize()
            synthetic_df = pd.read_csv(self.syn_csv_path)

            if not synthetic_df.empty:
                logging.info("Successful attack; found k = " + str(k))
                return k

        logging.info("Unsuccessful attack; could not determine k within 1 to " + str(upper_bound))
        return
