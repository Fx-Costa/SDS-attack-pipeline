from Utils.SamplerUtil import SamplerUtil
from Utils.ConversionUtil import ConversionUtil
from Synthesizers.SDSSynthesizer import SDSSynthesizer
from Analysers.SensitiveAnalyser import SensitiveAnalyser
import os
import logging

# Configurations
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(format='%(levelname)s\t%(asctime)s : %(message)s', level=logging.INFO, datefmt='%d-%m-%y %H:%M:%S')


def main():
    # Sample the NIST NATIONAL dataset
    n, m, cols = 5, -1, None
    sampler = SamplerUtil(SRC_DIR + "\\..\\..\\NIST dataset\\NATIONAL.csv")
    dataframe = sampler.sample(n, m, cols)

    # Perform initial analysis using SensitiveAnalyser to determine properties of the sensitive dataset
    sensitive_analyser = SensitiveAnalyser(dataframe)
    sensitive_analysis_df = sensitive_analyser.analyse()

    # Create a CSV file from sample, and a synthesis config from this CSV file
    converter = ConversionUtil(dataframe)
    sensitive_data_filepath = converter.dataframe_to_csv("test")
    syn_config_filepath = converter.dataframe_to_syn_config("value_seeded", 3)

    # Perform SDS synthesis using SDSSynthesizer
    synthesizer = SDSSynthesizer(syn_config_filepath)
    synthesizer.synthesize(verbose=False, aggregate=True, generate=True, evaluate=True)

    # Perform attack(s); to determine K and create leaks, by data poisoning
    # TODO: perform attack(s) here (FindKAttack / LeakAttack)

    # Perform final analysis using SyntheticAnalyser to determine properties of the synthetic dataset
    # TODO: perform analysis here (SyntheticAnalyser)


if __name__ == '__main__':
    main()
