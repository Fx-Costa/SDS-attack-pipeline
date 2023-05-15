import json
from Utils.ConfigUtil import ConfigUtil
from Utils.LoggerUtil import LoggerUtil
from lib.python_pipeline.src.showcase import runForConfig

logger = LoggerUtil.instance()


class SDSSynthesizer:
    """
    A class for synthesizing sensitive dataset into synthetic dataset using k-anonymity using Microsoft's Synthetic
    Data Showcase (SDS) python_pipeline.

    Methods: synthesize(),
    """
    def __init__(self):
        """
        Creates an instance of SDSSynthesizer given a path to a synthetic configuration file
        """
        self.config = ConfigUtil.instance()
        self.syn_config_path = self.config["SYNTHETIC"]["config_dir"] + self.config["GENERAL"]["name"] + ".json"
        self.dataset_dir = self.config["SYNTHETIC"]["dataset_dir"]
        self.last_flags = {"nav": True, "eval": True, "gen": True, "agg": True}
        self.round = 0

    def synthesize(self, aggregate=False, generate=False, evaluate=False, navigate=False):
        """
        Performs synthesis using the syn_config_file and with any keyword arguments:
        aggregate : whether to aggregate during synthesis (bool),
        generate : whether to generate during synthesis,
        evaluate : whether to evaluate during synthesis,
        navigate : whether to navigate during synthesis,
        assumes all by default.

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
        # Open and read the synthesis config (json) file
        file = open(self.syn_config_path, "r+")
        syn_config = json.load(file)

        # Construct synthesis flags from arguments:
        # A current flag can only be set if all prior flags are also set, e.g.:
        # Evaluate can only be set if Generate is set, which in turn, can only be set if Aggregate is set.
        syn_config["navigate"] = True
        syn_config["evaluate"] = True
        syn_config["generate"] = True
        syn_config["aggregate"] = True

        if navigate is False:
            syn_config["navigate"], self.last_flags["nav"] = False, False
            if evaluate is False:
                syn_config["evaluate"], self.last_flags["eval"] = False, False
                if generate is False:
                    syn_config["generate"], self.last_flags["gen"] = False, False
                    if aggregate is False:
                        syn_config["aggregate"], self.last_flags["agg"] = False, False

        # Determine, based on 'round', if current synthesis is a re-synthesis or not - for logging and output prefix
        self.round += 1
        if self.round < 2:
            logger.info("Successful synthesis; created synthetic dataset at: " + self.dataset_dir +
                        syn_config["prefix"] + ".tsv")
        else:
            # If the round > 1, we must be performing re-synthesis, hence change the prefix in the synthesis config,
            # to avoid overwriting previous synthetic datasets
            syn_config["prefix"] = syn_config["prefix"] + str(self.round - 1)
            logger.debug("Successful re-synthesis (" + str(self.round - 1) + "); created synthetic dataset at: " +
                         self.dataset_dir + syn_config["prefix"] + ".tsv")

        file.close()

        # Perform synthesis with given flags
        runForConfig(syn_config)

    def resynthesize(self):
        """
        Performs synthesis with the same flags as the previous synthesis, generating a new config in the process.
        The new config file's name will be appended the round number.

        :return: void
        """
        if self.round < 1:
            logger.error("Unsuccessful re-synthesis; cannot re-synthesize before a synthesis has completed")
        else:
            self.synthesize(self.last_flags["agg"], self.last_flags["gen"],
                            self.last_flags["eval"], self.last_flags["nav"])
