import os

# TODO: use python code (from python-pipeline/src/) instead of system commandos
# TODO: move format specific functionality to utils file

class SDSSynthesizer:
    """
    A class for synthesizing sensitive dataset into synthetic dataset using k-anonymity using Microsoft's Synthetic
    Data Showcase (SDS) python-pipeline.

    Methods: synthesize(),
    """
    def __init__(self, syn_config_filepath):
        """
        Creates an instance of SDSSynthesizer given a path to a synthetic configuration file

        :param syn_config_file: the synthetic configuration file path
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

        :param kwargs: keyword arguments
        :return: path to the created synthetic file (string)
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


""" 

def main():
    df, path = rd.main()
    #df, path = rd.sample("../NIST dataset/NATIONAL.csv", 5, 3, "")
    print("Creating configurations file...")
    rd.write_to_syn_config(df, "")
    print("Performing synthesization...")


def synthesize(config_filepath):
    #os.system("python python-pipeline/src/showcase.py config.json --v --agg --gen --eval")
    os.system("python python-pipeline/src/showcase.py " + config_filepath + " --v --agg --gen --eval")


def tsv_to_dataframe(filepath):
    return pd.read_csv(filepath)


if __name__ == '__main__':
    main()
    synthesize("configs/test.json")
"""