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

    def __init__(self, sensitive_dataset_df, sensitive_analysis_df, synthesizer):
        """
        Creates an instance of NaiveAttacker

        :param sensitive_dataset_df: the sensitive dataset pandas dataframe
        :param sensitive_analysis_df: a pandas dataframe as a result of a sensitive analysis
        :param synthesizer: a synthesizer object
        """
        self.sensitive_dataset_df = sensitive_dataset_df
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

    def determine_targets(self):
        pass

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

    def leak(self, k, target_index, sensitive_col):
        logger.info("Commencing attack; Injecting poisoned data, target_index=" + str(target_index) + "...")

        # Get target's sensitive data (except the sensitive_col; i.e. the unknown sensitive feature we wish to leak)
        target_data = self.sensitive_dataset_df.iloc[target_index].drop(sensitive_col, axis=0)

        # Get the data types identified during the sensitive analysis
        sensitive_analysis_df_types = self.sensitive_analysis_df.loc["type"]

        # Construct the payload
        payload = {}
        for index in target_data.index:
            # Get the data type of 'column' from sensitive_analysis_df_types
            data_type = sensitive_analysis_df_types[index]

            if data_type == np.dtype(np.object):
                # If the data type is object, no casting is required
                payload[index] = target_data[index]
            else:
                # Cast values from target_data to the data type and insert into payload
                casted_values = target_data[index].astype(data_type).tolist()
                payload[index] = casted_values

        # Create a dataframe from the payload repeated k times
        payload_df = pd.DataFrame([payload])
        payload_df = pd.concat([payload_df] * (k - 1), ignore_index=True)

        # Create injection labels; i0, ..., ik
        payload_df.rename(index=lambda i: f'i{i}', inplace=True)

        # Perform injection into sensitive dataset
        self.inject(pd.DataFrame(payload_df, columns=self.sensitive_analysis_df.columns))

        # Perform resynthesization of sensitive dataset
        self.synthesizer.resynthesize()

        #TODO: Should apply a brute-force to the sensitive (unknown) column/feature
