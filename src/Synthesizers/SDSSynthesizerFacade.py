from src.Utils.ConfigUtil import ConfigUtil
from src.Utils.LoggerUtil import LoggerUtil
from lib.python_pipeline.src.showcase import runForConfig
from src.File.SynthesisConfigFile import SynthesisConfigFile

logger = LoggerUtil.instance()
config = ConfigUtil.instance()


class SDSSynthesizerFacade:
    """
    A class for synthesizing sensitive dataset into synthetic dataset using k-anonymity using Microsoft's Synthetic
    Data Showcase (SDS) python_pipeline (see /lib).
    """

    def __init__(self, synthesis_config_file: SynthesisConfigFile):
        """
        Initializes an instance of SDSSynthesizerFacade using a synthetic_dataset_file.
        """
        # Initialize a private member of type SyntheticConfig
        self.synthesis_config_file = synthesis_config_file

        # Initialize flags for keeping track of previous syntheses
        self.__flags = {"navigate": True, "evaluate": True, "generate": True, "aggregate": True}
        self.__round = 0

    def synthesize(self, aggregate=False, generate=False, evaluate=False, navigate=False):
        """
        Performs synthesis using the SynthesisConfigFile and SyntheticDatasetFile and by using the flags:
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
        # Construct synthesis flags from arguments:
        # A current flag can only be set if all prior flags are also set, e.g.:
        # Evaluate can only be set if Generate is set, which in turn, can only be set if Aggregate is set.
        if navigate is False:
            self.__flags["navigate"] = navigate
            if evaluate is False:
                self.__flags["evaluate"] = evaluate
                if generate is False:
                    self.__flags["generate"] = generate
                    if aggregate is False:
                        self.__flags["aggregate"] = aggregate

        # Determine whether a resynthesis, if so writes the synthetic dataset to another file
        is_resynthesis = self.__round > 0

        # Write the flags to the synthesis config
        self.synthesis_config_file.write(self.__flags, is_resynthesis=is_resynthesis)

        synthesis_config = self.synthesis_config_file.read(is_resynthesis=is_resynthesis)
        logger.debug("Successful synthesis (" + str(self.__round) + "); created synthetic dataset: " +
                     synthesis_config["output_dir"])
        self.__round += 1

        # Perform synthesis with the synthesis_config_file
        runForConfig(synthesis_config)

    def resynthesize(self):
        """
        Performs synthesis with the same flags as the previous synthesis, generating a new config in the process.
        The new config file's name will be prefixed by 'resynthesis'.
        """
        if self.__round < 1:
            logger.error("Unsuccessful re-synthesis; cannot re-synthesize before a synthesis has completed")
        else:
            self.synthesize(self.__flags["aggregate"], self.__flags["generate"],
                            self.__flags["evaluate"], self.__flags["navigate"])
