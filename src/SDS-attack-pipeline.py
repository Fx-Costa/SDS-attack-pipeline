import logging

from Utils.SamplerUtil import SamplerUtil
from Utils.ConversionUtil import ConversionUtil
from Synthesizers.SDSSynthesizer import SDSSynthesizer
from Analysers.SensitiveAnalyser import SensitiveAnalyser
from Attacks.FindKAttack import FindKAttack
from Utils.ConfigUtil import ConfigUtil


def main():
    config = ConfigUtil.instance()
    if config["LOGGING"]["enabled"]:
        logging.basicConfig(level=config["LOGGING"]["level"],
                            format=config["LOGGING"]["format"],
                            datefmt=config["LOGGING"]["date_format"])

    # Sample the NIST NATIONAL dataset
    n, m, cols = 6, -1, None
    sampler = SamplerUtil()
    sample_df = sampler.sample(n, m, cols)

    # Perform initial analysis using SensitiveAnalyser to determine properties of the sensitive dataset
    sensitive_analyser = SensitiveAnalyser(sample_df)
    sensitive_analysis_df = sensitive_analyser.analyse()

    # Create a CSV file from sample, and a synthesis config from this CSV file
    converter = ConversionUtil(sample_df)
    converter.dataframe_to_csv()
    converter.dataframe_to_syn_config("row_seeded", k=4)

    # Perform SDS synthesis using SDSSynthesizer
    synthesizer = SDSSynthesizer()
    synthesizer.synthesize(verbose=False, aggregate=True, generate=True, evaluate=True)

    # Perform attack(s); to determine K and create leaks, by data poisoning
    # TODO: perform attack(s) here (FindKAttack / LeakAttack)
    attack1 = FindKAttack(sensitive_analysis_df.columns, synthesizer)
    k = attack1.find_k()

    # Perform final analysis using SyntheticAnalyser to determine properties of the synthetic dataset
    # TODO: perform analysis here (SyntheticAnalyser)


if __name__ == '__main__':
    main()
