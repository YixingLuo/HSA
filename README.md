# Hierarchical Safety Assessment (HSA)
Autonomous Driving Systems (ADSs) are complex systems that must satisfy multiple safety requirements. In particular cases, all the requirements cannot be satisfied at the same time, and the control software of the ADS must make trade-offs among their satisfaction. Usually, the trading-offs in the ADS decision-making process are configurable; different ADS configurations can affect driving behaviors, satisfying or violating requirements at different degrees. Therefore, it is highly important to know whether an ADS configuration can guarantee a safe drive or not. We propose *Hierarchical Safety Assessment* (HSA) to quantitatively analyze violation severity of safety requirements and distinguish safer ADS configurations based on the requirements violations comparison done in a hierarchical way by following requirements importance.

Specifically:
- HSA helps the user to establish a quantitative model for the different requirements of the ADS under study (e.g., the *safety metrics* reported in *Appendix.pdf* for the ADS under study). This step must be performed by the user by considering the specific ADS.
- Given the definitions of the safety metrics, HSA automatically works as follows:
  - it runs the ADS under study over a given set of *test scenarios* using a set of possible ADS *configurations*. This step produces a set of *test results*, in terms of test logs of the simulations;
  - it applies *Requirements Violation Analysis* (RVA), that, for all the test results, assesses the satisfaction of the different requirements using the *safety metrics*;
  - it applies a hierarchical comparison technique, *Requirements Violation Comparison* (RVC) that, given two ADS configurations *c* and *c'*, tries to establish which one is safer. It does so by comparing the RVA results of all the tests of *c* and *c'*;
  - finally, given the results of all the pairwise comparisons, it ranks the ADS configurations from the perspective of violations of the safety requirements.

In the following, we describe the structure of the repository.

## Appendix.pdf
This file contains the evaluation functions of all seven requirements descripted in the paper, i.e., Vehicle Stability, Safe Distance, Compliance, and Smoothness, and the proof of the transitivity of Requirements Violation Comparison.

## Codes
This folder contains the code of the baseline approach *Conservative Comparison* and *Hierarchical Safety Assessment* (HSA) used in experimental evaluations. However, as the system under study is provided by our industrial partner, for confidentiality reasons we cannot share the code of the autonomous driving system we used in the experiments. Still for confidentiality reasons, we cannot provide the ADS scenarios used as input of the approach.

## Results_RVA
This folder provides the normalized RVA results of the seven requirements listed in "Appendix.pdf" in 10000 test scenarios under different configurations of the ADS provided by our industry partner in six traffic situations.

## Results_ConservativeComparison
This folder contains all comparison results of 60 modified ADS configurations and of the original configuration obtained using the *Conservative Comparison* approach.

## Results_HSA
This folder contains all comparison results of 60 modified ADS configurations and the original configuration obtained using the HSA approach.

## Analysis_HSA_results
This folder contains the heat maps showing the Spearman correlation between configuration options and requirements violation severity in six traffic situations (see RQ3 in the paper).


## Authors Information

### Authors List

- Yixing Luo, Peking University, China
- Xiao-Yi Zhang, National Institute of Informatics, Japan
- Paolo Arcaini, National Institute of Informatics, Japan
- Zhi Jin, Peking University, China
- Haiyan Zhao, Peking University, China
- Linjuan Zhang, Peking University, China
- Fuyuki Ishikawa, National Institute of Informatics, Japan

### How to cite this work

Y. Luo et al., "Hierarchical Assessment of Safety Requirements for Configurations of Autonomous Driving Systems," 2022 IEEE 30th International Requirements Engineering Conference (RE), 2022.


## Artifact Location

The artifact of HSA is available in a GitHub repo [HSA], and on the Zenodo [DOI]. 

[HSA]: https://github.com/YixingLuo/Hierarchical-Safety-Assessment

[DOI]: https://zenodo.org/record/6559042#.YoT3fOhByUk
