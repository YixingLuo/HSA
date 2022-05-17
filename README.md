# Hierarchical-Safety-Assessment
Autonomous Driving Systems (ADSs) are complex systems that must satisfy multiple safety requirements. Usually, the trading-offs in the decision-making process are configurable; different configuration options can affect driving behaviors, satisfying or violating requirements at different degrees. Therefore, it is highly important to know whether a configuration can guarantee a safe drive or not Hierarchical Safety Assessment (HSA) is proposed to quantitatively analyze violation severity of safety requirements and distinguish safer ADS configurations based on the requirements violations comparison done in a hierarchical way by following requirements importance.

Specifically, HSA helps you to:

- Establish a quantitative model, Requirements Violation Analysis (RVA), to analyze violations of safety requirements in specific scenarios for the differently configured ADS.

- Leverage a hierarchical comparison technique, Requirements Violation Comparison (RVC), to compare the analysis results of RVA for the ADS under different pairs of configurations in a systematic way.

Hierarchical Safety Assessment (HSA) is an assessment approach, which combines the results of RVA and RVC to rank the ADS configurations from the perspective of violations of the safety requirements.

### 1. Appendix.pdf
The file contains the evaluation functions of all seven requirements descripted in the paper, i.e., Vehicle Stability, Safe Distance, Compliance, and Smoothness, and the proof of the transitivity of Requirements Violation Comparison.

### 2. The file folders:

#### Codes: 
We provide the code of baseline approach Conservative Comparison and Hierarchical Safety Assessment (HSA) used in experimental evaluations. However, as the case study system is provided by our industrial partner for commercial use, we do not share the codes for the autonomous driving system we used.

#### Results_RVA: 
This folder provides the normalized RVA results of seven requirements listed in "Appendix.pdf" in 10000 test scenarios under different configurations of the ADS provided by our industry partner in six traffic situations.

#### Results_ConservativeComparison: 
The all comparison results of 60 modified ADS configurations and the original one under Conservative Comparison.

#### Results_HSA: 
The all comparison results of 60 modified ADS configurations and the original one under HSA.

#### Usefulness_Of_HSA: 
The heat maps show the Spearman correlation between configuration options and requirements violation severity in six traffic situations.


## Authors Information

### Author List

Yixing Luo, Xiao-Yi Zhang, Paolo Arcaini, Zhi Jin, Haiyan Zhao, Linjuan Zhang, Fuyuki Ishikawa

### How to cite this work

Y. Luo et al., "Hierarchical Assessment of Safety Requirements for Configurations of Autonomous Driving Systems," 2022 IEEE 30th International Requirements Engineering Conference (RE), 2022.


## Artifact Location

The artifact of HSA is available in a GitHub repo [HSA], and on the Zenodo [DOI]. 

[HSA]: https://github.com/YixingLuo/Hierarchical-Safety-Assessment

[DOI]: https://doi.org/10.5281/zenodo.6544894

