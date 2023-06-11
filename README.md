# SDS-attack-pipeline
A Python pipeline tool for analysis and attacks (data poisoning) on the SDS (k-anonymity) synthesis

## Prerequisites
- lib-python (SDS)
- python-pipeline (SDS)
- core (SDS)
- rustc compiler (https://www.rust-lang.org/)
- maturin
- NIST dataset

## Usage
- Set the required configurations in `Config.ini`, including:
  - `dataset_path` an absolute path to the sensitive dataset
  - `name` to set the prefix of generated files
  - `root_dir` an absolute path to the root of the project
- Optional configurations in `Config.ini`:
    - verbose logging output (includes logging from all sources)
    - logging level and formatting
- Run main program `SDS-attack-pipeline` through IDE and or commandline:

`x`

## Structure of the pipeline
![pipeline](pipeline-diagram.png)

## Flow of attack
![pipeline](flow.png)