import os
import logging
from Utils.ConfigUtil import ConfigUtil

# TODO: use python code (from python-pipeline/src/) instead of system commandos


class SDSSynthesizer:
    """
    A class for synthesizing sensitive dataset into synthetic dataset using k-anonymity using Microsoft's Synthetic
    Data Showcase (SDS) python-pipeline.

    Methods: synthesize(),
    """
    def __init__(self):
        """
        Creates an instance of SDSSynthesizer given a path to a synthetic configuration file
        """
        self.syn_config_filepath = ConfigUtil.instance()["SYNTHETIC"]["config_dir"]
        self.flags = {"verb": False, "agg": True, "gen": True, "eval": True, "nav": True}

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
            self.flags["verb"] = True

        # A current flag can only be set if all prior flags are also set, e.g.:
        # Evaluate can only be set if Generate is set, which in turn, can only be set if Aggregate is set.
        if navigate is False:
            flags = flags[:-(len(" --navigate"))]
            self.flags["nav"] = False
            if evaluate is False:
                flags = flags[:-(len(" --evaluate"))]
                self.flags["eval"] = False
                if generate is False:
                    flags = flags[:-(len(" --generate"))]
                    self.flags["gen"] = False
                    if aggregate is False:
                        flags = flags[:-(len(" --aggregate"))]
                        self.flags["agg"] = False

        # Perform synthesis with given flags
        # TODO: generalize this
        os.system("python ../python-pipeline/src/showcase.py " + "../configs/test.json" + flags)
        logging.info("Successful synthesis; created " + self.syn_config_filepath)
        # TODO: using python-pipeline, return or set self to the synthetic dataset path

    def resynthesize(self):
        """
        Performs synthesis with the same flags as the previous synthesis
        :return: void
        """
        if self.flags is None:
            logging.info("Unsuccessful re-synthesis; cannot re-synthesize before a synthesis has completed")
        else:
            self.synthesize(self.flags["verb"], self.flags["agg"], self.flags["gen"],
                            self.flags["eval"], self.flags["nav"])
            logging.info("Successful re-synthesis; created " + self.syn_config_filepath)
