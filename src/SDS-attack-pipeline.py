from Utils.SamplerUtil import SamplerUtil
from Utils.ConversionUtil import ConversionUtil
from Synthesizers.SDSSynthesizer import SDSSynthesizer
# TODO: get root path and use this instead as input to SamplerUtil
# TODO: Logging


def main():
    # Sample the NIST NATIONAL dataset
    sampler = SamplerUtil("..\\..\\NIST dataset\\NATIONAL.csv")
    dataframe = sampler.sample(5, 3, ["SEX", "AGEP", "PUMA"])

    # Perform initial analysis using SensitiveAnalyser to determine properties of the sensitive dataset
    # TODO: perform analysis here (SensitiveAnalyser)

    # Create a CSV file from sample, and a synthesis config from this CSV file
    converter = ConversionUtil(dataframe)
    sensitive_data_filepath = converter.dataframe_to_csv("test")  # TODO: use identifier found from SensitiveAnalyser as input instead
    syn_config_filepath = converter.dataframe_to_syn_config("value_seeded", 3)

    # Perform SDS synthesis using SDSSynthesizer
    synthesizer = SDSSynthesizer(syn_config_filepath)
    synthesizer.synthesize(verbose=True, aggregate=True, generate=True, evaluate=True)

    # Perform attack(s); to determine K and create leaks, by data poisoning
    # TODO: perform attack(s) here (FindKAttack / LeakAttack)

    # Perform final analysis using SyntheticAnalyser to determine properties of the synthetic dataset
    # TODO: perform analysis here (SyntheticAnalyser)


if __name__ == '__main__':
    main()
