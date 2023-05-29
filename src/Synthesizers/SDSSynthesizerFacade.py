import json
from Utils.ConfigUtil import ConfigUtil
from Utils.LoggerUtil import LoggerUtil
from lib.python_pipeline.src.showcase import runForConfig

logger = LoggerUtil.instance()
config = ConfigUtil.instance()


class SDSSynthesizerFacade:
    """
    A class for synthesizing sensitive dataset into synthetic dataset using k-anonymity using Microsoft's Synthetic
    Data Showcase (SDS) python_pipeline.

    Methods: synthesize(),
    """

    def __init__(self):
        """
        Initializes an instance of SDSSynthesizerFacade.

        :return: SDSSynthesizerFacade
        """
        # Initialize a private member of type SyntheticConfig
        self.__syn_config_path = config["SYNTHETIC"]["config_dir"] + config["GENERAL"]["name"] + ".json"

        # Initialize a private member of type SyntheticDataset
        self.dataset_dir = config["SYNTHETIC"]["dataset_dir"]

        # Initialize a SyntheticDataset
        self.last_flags = {"nav": True, "eval": True, "gen": True, "agg": True}
        self.round = 0

    def synthesize(self, aggregate=False, generate=False, evaluate=False, navigate=False):
        """
        Performs synthesis using the SyntheticConfigFile.py pointed to by config_dir (in Config.ini) with the identifier 'name'
        (in Config.ini), using the flags:
            aggregate : whether to perform aggregate step during synthesis (aggregate counts),
            generate : whether to perform generation step during synthesis (microdata),
            evaluate : whether to perform evaluation step during synthesis (statistics),
            navigate : whether to perform navigation step during synthesis (PowerBI),
        all are assumed by default.

        :param aggregate: boolean
        :param generate: boolean
        :param evaluate: boolean
        :param navigate: boolean
        """
        # Open and read the synthesis config (json) file
        file = open(self.__syn_config_path, "r+")
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
            syn_config["prefix"] = syn_config["prefix"] + "_resynthesis"
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
