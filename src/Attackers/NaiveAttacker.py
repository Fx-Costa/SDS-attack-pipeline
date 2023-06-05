import numpy as np
import pandas as pd
from Utils.LoggerUtil import LoggerUtil
from Analyzers.SyntheticAnalyzer import SyntheticAnalyzer
from File.SyntheticDatasetFile import SyntheticDatasetFile
from File.SensitiveDatasetFile import SensitiveDatasetFile
from Synthesizers.SDSSynthesizerFacade import SDSSynthesizerFacade

logger = LoggerUtil.instance()


class NaiveAttacker:
    """
    A class for naive attacks on a SDS synthesized dataset
    """

    def __init__(self, sensitive_dataset_file: SensitiveDatasetFile, synthetic_dataset_file: SyntheticDatasetFile,
                 sensitive_analysis: pd.DataFrame, synthesizer: SDSSynthesizerFacade):
        self.sensitive_dataset_file = sensitive_dataset_file
        self.synthetic_dataset_file = synthetic_dataset_file
        self.sensitive_analysis = sensitive_analysis
        self.synthesizer = synthesizer

    def __inject(self, data):
        """
        Injects dataframe into the sensitive dataset by writing to the sensitive dataset (always appends), and returns
            number of rows injected.

        :param data: dataframe
        :return: integer
        """
        self.sensitive_dataset_file.write(data, include_header=False)
        return data.shape[0]

    def __construct_payload(self, known_data, sensitive_col, value, repetitions):
        # Get properties identified in the sensitive dataset during the sensitive analysis
        data_types = self.sensitive_analysis.loc["type"]

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
            elif known_data[index] == "N":
                # If we are using only QIs the value "N" indicates that the value for this column should not be included
                payload[index] = np.NaN
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
        data_type = self.sensitive_analysis.at["type", sensitive_col]
        minimum = self.sensitive_analysis.at["min", sensitive_col]
        val_outside_domain = np.dtype(data_type).type(minimum) - 1

        # Accumulators and flags used to identify leaks and thresholds
        is_leaked = False
        injection_count = 0

        # Determine k
        while not is_leaked:
            # Construct a payload with NaN values to not interfere.
            # Inject it into the dataset and keep track of the number of injections
            payload = self.__construct_payload(known_data, sensitive_col, val_outside_domain, 1)
            injection_count += self.__inject(pd.DataFrame(payload, columns=self.sensitive_analysis.columns))

            # Apply synthesis
            self.synthesizer.resynthesize()

            # Analyze the synthesized dataset using the SyntheticAnalyser to determine if a leak of the payload occurred
            is_leaked = SyntheticAnalyzer(self.synthetic_dataset_file).analyze(payload)

        # The value of k is the number of identical injections that resulted in a leak
        logger.info("Successful attack; found K=" + str(injection_count))
        return injection_count

    def determine_sensitive_value(self, sensitive_col, known_data, k):
        logger.info("Commencing attack; Injecting poisoned data to find sensitive value(s)...")

        # Get properties of the sensitive column found during the SensitiveAnalysis
        data_type = self.sensitive_analysis.at["type", sensitive_col]
        minimum = self.sensitive_analysis.at["min", sensitive_col]
        maximum = self.sensitive_analysis.at["max", sensitive_col]
        minimum = np.dtype(data_type).type(minimum)
        maximum = np.dtype(data_type).type(maximum)

        potential_sensitive_values = []

        # Determine the range of values to iterate during the bruteforce
        sensitive_range = np.arange(minimum, maximum + 1)

        # Determine the sensitive values by bruteforce
        for potential_sensitive_value in sensitive_range:
            # Construct a payload with potential value (we use minimum as the accumulator)
            # Inject it into the dataset, the injection_count will always increment by k
            payload = self.__construct_payload(known_data, sensitive_col, potential_sensitive_value, k - 1)
            self.__inject(pd.DataFrame(payload, columns=self.sensitive_analysis.columns))

            # Apply synthesis
            self.synthesizer.resynthesize()

            # Analyze the synthesized dataset using the SyntheticAnalyser to determine if a leak of the payload occurred
            is_leaked = SyntheticAnalyzer(self.synthetic_dataset_file).analyze(payload)

            # If the payload resulted in a leak, add the guessed sensitive value to the result
            if is_leaked:
                potential_sensitive_values.append(potential_sensitive_value)

        # If we found no potential sensitive values, it must be because it is NaN
        if len(potential_sensitive_values) < 1:
            potential_sensitive_values.append(np.nan)

        logger.info("Successful attack; found sensitive value(s): " + str(potential_sensitive_values))
        return potential_sensitive_values

    def attack_loop(self, sensitive_col, known_cols=None):
        # Assure that the sensitive_col is an incremental type
        sensitive_type = self.sensitive_analysis[sensitive_col].loc["type"]
        if sensitive_type == np.object:
            logger.error("Failed to run attack_loop; sensitive_col=" + sensitive_col + " is of an invalid type")
            return

        # We simulate the known data by taking the data from the first row, i.e. the target is the first row.
        if known_cols is None:
            # We use all non-sensitive columns (the sensitive column is discarded later)
            known_data = self.sensitive_dataset_file.read().iloc[0]
        else:
            # We use all data on known columns (intended to be the QIs)
            target_data = self.sensitive_dataset_file.read().iloc[0]

            # Get and modify the values on the unknown columns to NaN
            unknown_cols = [col for col in target_data.index if col not in known_cols and col != sensitive_col]
            target_data.loc[unknown_cols] = "N"

            known_data = pd.Series(target_data)

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
                    " Leaked " + str(num_potential_sensitive_values - 1) + " other entries during the attack.")

        return sensitive_values, k
