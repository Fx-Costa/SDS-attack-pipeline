import os
import logging

# TODO: use python code (from python-pipeline/src/) instead of system commandos


class SDSSynthesizer:
    """
    A class for synthesizing sensitive dataset into synthetic dataset using k-anonymity using Microsoft's Synthetic
    Data Showcase (SDS) python-pipeline.

    Methods: synthesize(),
    """
    def __init__(self, syn_config_filepath):
        """
        Creates an instance of SDSSynthesizer given a path to a synthetic configuration file

        :param syn_config_filepath: the synthetic configuration file path
        """
        self.syn_config_filepath = syn_config_filepath

    def synthesize(self, verbose=False, aggregate=False, generate=False, evaluate=False, navigate=False):
        """
        Performs synthesis using the syn_config_file and with any keyword arguments:
        verbose : whether to use verbose output of logs (bool),
        aggregate : whether to aggregate during synthesis (bool),
        generate : whether to generate during synthesis,
        evaluate : whether to evaluate during synthesis,
        navigate : whether to navigate during synthesis,
        assumes all except verbose if none are given.

        :param verbose: whether to output synthesis logs
        :param aggregate: whether to perform aggregation step
            (generates protected counts of records [reportable_aggregates])
        :param generate: whether to perform generation step
            (generates synthetic dataset [synthetic_microdata])
        :param evaluate: whether to perform evaluation step
            (evaluates synthetic dataset wrt. sensitive dataset [stats])
        :param navigate: whether to perform navigation step
            (generates Power BI template from synthetic and aggregate data)
        :return: void
        """
        # Construct synthesis flags from arguments
        flags = " --aggregate --generate --evaluate --navigate"
        if verbose is True:
            flags = " --verbose" + flags

        # A current flag can only be set if all prior flags are also set, e.g.:
        # Evaluate can only be set if Generate is set, which in turn, can only be set if Aggregate is set.
        if navigate is False:
            flags = flags[:-(len(" --navigate"))]
            if evaluate is False:
                flags = flags[:-(len(" --evaluate"))]
                if generate is False:
                    flags = flags[:-(len(" --generate"))]
                    if aggregate is False:
                        flags = flags[:-(len(" --aggregate"))]

        # Perform synthesis with given flags
        # TODO: generalize this
        os.system("python ../python-pipeline/src/showcase.py " + "../configs/test.json" + flags)
        logging.info("Successful synthesis; created " + self.syn_config_filepath)
