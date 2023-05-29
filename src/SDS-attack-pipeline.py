import numpy as np

from Utils.SamplerUtil import SamplerUtil
from Utils.ConversionUtil import ConversionUtil
from Synthesizers.SDSSynthesizerFacade import SDSSynthesizerFacade
from Analysers.SensitiveAnalyser import SensitiveAnalyser
from Attackers.NaiveAttacker import NaiveAttacker


def main():
    # Sample the NIST dataset
    n, m, cols = 300, 5, None
    sample_df = SamplerUtil().sample(n, m, cols)

    # Perform initial analysis using SensitiveAnalyser to determine properties of the sensitive dataset
    sensitive_analyser = SensitiveAnalyser(sample_df)
    sensitive_analysis_df = sensitive_analyser.analyse()

    # Create a CSV file from sample, and a SDS synthesis config from this CSV file
    converter = ConversionUtil(sample_df)
    converter.dataframe_to_csv()
    converter.dataframe_to_syn_config("row_seeded", k=9)

    # Perform SDS synthesis using SDSSynthesizer
    synthesizer = SDSSynthesizerFacade()
    synthesizer.synthesize(aggregate=True, generate=True)

    # Perform attack(s); to determine K and create leaks by data poisoning
    naive_attacker = NaiveAttacker(sample_df, sensitive_analysis_df, synthesizer)
    value, k = naive_attacker.attack_loop(sensitive_col="MSP")


if __name__ == '__main__':
    main()
