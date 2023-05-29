import numpy as np
import pandas as pd
from Utils.SamplerUtil import SamplerUtil
from Utils.ConversionUtil import ConversionUtil
from Utils.ConfigUtil import ConfigUtil
from Utils.LoggerUtil import LoggerUtil
from Analysers.SyntheticAnalyser import SyntheticAnalyser

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
        self.syn_csv_path = self.config["SYNTHETIC"]["dataset_dir"] + self.config["GENERAL"]["name"] \
            + "_synthetic_microdata.tsv"

    def inject(self, dataframe):
        """
        Injects a Pandas dataframe into the sensitive dataset (often a sample) by appending to it

        :param dataframe: a pandas dataframe to 'inject' (append) to the sensitive dataset
        :return: void
        """
        dataframe.to_csv(self.config["SENSITIVE"]["sample_dir"] + self.config["GENERAL"]["name"] + ".csv",
                         mode='a', header=False)
        logger.debug("Performed injection; Appended " + str(dataframe.shape[0]) + " rows to sensitive dataset")
        return dataframe.shape[0]

    def construct_payload(self, known_data, sensitive_col, value, repetitions):
        # Get properties identified in the sensitive dataset during the sensitive analysis
        data_types = self.sensitive_analysis_df.loc["type"]

        payload = {}
        for index in known_data.index:
            # Get the data type of 'column' from sensitive_analysis_df_types
            data_type = data_types[index]

            # If the index is the sensitive column, we do not just insert the value, instead we insert a potential value
            # To simulate that the sensitive value is unknown
            if index == sensitive_col:
                # Insert a guess for the sensitive attribute
                payload[sensitive_col] = value
                continue

            if data_type == np.dtype(np.object):
                # If the data type is object, no casting is required
                payload[index] = known_data[index]
            else:
                # Cast values from target_data to the appropriate data type and insert into payload
                casted_values = known_data[index].astype(data_type).tolist()
                payload[index] = casted_values

        # Create a dataframe from the payload repeated k times
        payload_df = pd.DataFrame([payload])
        payload_df = pd.concat([payload_df] * repetitions, ignore_index=True)

        # Create injection label; 'i'k
        payload_df.rename(index=lambda i: f'i{i}', inplace=True)

        return payload_df

    def determine_k(self, sensitive_col, known_data):
        logger.info("Commencing attack; Injecting poisoned data to find K...")

        # Get properties of the sensitive column found during the SensitiveAnalysis
        data_type = self.sensitive_analysis_df.at["type", sensitive_col]
        minimum = self.sensitive_analysis_df.at["min", sensitive_col]
        val_outside_domain = np.dtype(data_type).type(minimum) - 1

        # Accumulators and flags used to identify leaks and thresholds
        is_leaked = False
        injection_count = 0

        # Determine k
        while not is_leaked:
            # Construct a payload with NaN values to not interfere.
            # Inject it into the dataset and keep track of the number of injections
            payload = self.construct_payload(known_data, sensitive_col, val_outside_domain, 1)
            injection_count += self.inject(pd.DataFrame(payload, columns=self.sensitive_analysis_df.columns))

            # Apply synthesis
            self.synthesizer.resynthesize()

            # Analyze the synthesized dataset using the SyntheticAnalyser to determine if a leak of the payload occurred
            is_leaked = SyntheticAnalyser().determine_leak(payload)

        # The value of k is the number of identical injections that resulted in a leak
        logger.info("Successful attack; found K=" + str(injection_count))
        return injection_count

    def determine_sensitive_value(self, sensitive_col, known_data, k):
        logger.info("Commencing attack; Injecting poisoned data to find sensitive value(s)...")

        # Get properties of the sensitive column found during the SensitiveAnalysis
        data_type = self.sensitive_analysis_df.at["type", sensitive_col]
        is_nan = self.sensitive_analysis_df.at["NaN", sensitive_col]
        minimum = self.sensitive_analysis_df.at["min", sensitive_col]
        maximum = self.sensitive_analysis_df.at["max", sensitive_col]
        minimum = np.dtype(data_type).type(minimum)
        maximum = np.dtype(data_type).type(maximum)

        potential_sensitive_values = []

        # Determine the range of values to iterate during the bruteforce
        sensitive_range = np.arange(minimum, maximum + 1)

        # Determine the sensitive values by bruteforce
        for potential_sensitive_value in sensitive_range:
            # Construct a payload with potential value (we use minimum as the accumulator)
            # Inject it into the dataset, the injection_count will always increment by k
            payload = self.construct_payload(known_data, sensitive_col, potential_sensitive_value, k - 1)
            self.inject(pd.DataFrame(payload, columns=self.sensitive_analysis_df.columns))

            # Apply synthesis
            self.synthesizer.resynthesize()

            # Analyze the synthesized dataset using the SyntheticAnalyser to determine if a leak of the payload occurred
            is_leaked = SyntheticAnalyser().determine_leak(payload)

            # If the payload resulted in a leak, add the guessed sensitive value to the result
            if is_leaked:
                potential_sensitive_values.append(potential_sensitive_value)

        # If we found no potential sensitive values, it must be because it is NaN
        if len(potential_sensitive_values) < 1:
            potential_sensitive_values.append(np.nan)

        logger.info("Successful attack; found sensitive value(s): " + str(potential_sensitive_values))
        return potential_sensitive_values

    def attack_loop(self, sensitive_col):
        # We simulate the known data by taking the data from the first row, i.e. the target is the first row.
        known_data = self.sensitive_dataset_df.iloc[0]
        logger.info("Starting attack_loop; sensitive_col=" + sensitive_col + ", known data of target: " +
                    str(dict(known_data.drop(sensitive_col, axis=0))))

        # Determine K and potential sensitive values
        k = self.determine_k(sensitive_col, known_data)
        sensitive_values = self.determine_sensitive_value(sensitive_col, known_data, k)

        # Determine the implied certainty of having found the correct sensitive value
        num_potential_sensitive_values = len(sensitive_values)
        certainty = 100
        if num_potential_sensitive_values != 0:
            certainty = round(100 / num_potential_sensitive_values, 2)

        logger.info("Completed attack_loop; found K=" + str(k) + " and sensitive value(s): " +
                    str(sensitive_values) + ", implying a " + str(certainty) + "% certainty." +
                    " Leaked " + str(num_potential_sensitive_values - 1) + " other entries during the bruteforce.")

        return sensitive_values, k
