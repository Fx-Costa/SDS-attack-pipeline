import pandas as pd
from Utils.SamplerUtil import SamplerUtil
from Utils.ConversionUtil import ConversionUtil
from Utils.ConfigUtil import ConfigUtil
from Utils.LoggerUtil import LoggerUtil

logger = LoggerUtil.instance()


class NaiveAttacker:
    """
    A class for naive attacks on a SDS synthesized dataset

    Methods: sample()
    """

    def __init__(self, cols, synthesizer):
        """
        Creates an instance of NaiveAttacker
        :param cols: a list of column names (strings)
        :param synthesizer: a synthesizer object
        """
        self.cols = cols
        self.synthesizer = synthesizer
        config = ConfigUtil.instance()
        self.syn_csv_path = config["SYNTHETIC"]["dataset_dir"] + config["GENERAL"]["name"] + "_synthetic_microdata.tsv"

    def find_k(self, upper_bound=10):
        """
        Finds K of a synthetic dataset.
        Assumes that re-synthesis is possible with identical config. i.e. the syn_config is known.
        :return:
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

    def leak(self):
        pass
