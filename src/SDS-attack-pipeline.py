from File.SensitiveDatasetFile import SensitiveDatasetFile
from File.SynthesisConfigFile import SynthesisConfigFile
from Utils.SamplerUtil import SamplerUtil
from Analyzers.SensitiveAnalyzer import SensitiveAnalyzer
from File.SyntheticDatasetFile import SyntheticDatasetFile
from Synthesizers.SDSSynthesizerFacade import SDSSynthesizerFacade
from Attackers.NaiveAttacker import NaiveAttacker


def main():
    # Create the file objects (generates directories and files at root)
    sensitive_dataset_file = SensitiveDatasetFile()
    synthetic_dataset_file = SyntheticDatasetFile()

    # Create sensitive dataset
    sample = SamplerUtil().sample(n=6, m=5, cols=None)
    sensitive_dataset_file.write(sample)

    # Perform analysis on the sensitive dataset to determine properties
    sensitive_analysis = SensitiveAnalyzer(sensitive_dataset_file).analyze(sample)

    # Create synthesis configuration
    synthesis_config_file = SynthesisConfigFile(sensitive_dataset_file, synthetic_dataset_file)
    synthesis_config_file.write({"reporting_resolution": 3, "synthesis_mode": "value_seeded"})

    # Create synthetic dataset
    synthesizer = SDSSynthesizerFacade(synthesis_config_file)
    synthesizer.synthesize(aggregate=True, generate=True)

    # Perform attack-loop to bruteforce k and the sensitive value by data poisoning
    naive_attacker = NaiveAttacker(sensitive_dataset_file, synthetic_dataset_file, sensitive_analysis, synthesizer)
    naive_attacker.attack_loop(sensitive_col="MSP")


if __name__ == '__main__':
    main()
