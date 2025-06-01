# :mega: ChatUnitest

![logo](docs/img/logo.png)

## Background
Many people have tried using ChatGPT to help them with various programming tasks and have achieved good results. However, there are some issues with using ChatGPT directly. Firstly, the generated code often fails to execute correctly, leading to the famous saying **"five minutes to code, two hours to debug"**. Secondly, it is inconvenient to integrate with existing projects as it requires manual interaction with ChatGPT and switching between different platforms.

ChatUniTest is an innovative framework designed to improve automated unit test generation. ChatUniTest utilizes an LLM-based approach enhanced with **"adaptive focal context"** mechanism to encompass valuable
context in prompts and adheres to a **"Generation-Validation-Repair"** mechanism to rectify errors in generated unit tests. 
we have developed ChatUniTest Core, a common library that implements the core workflow, complemented by the ChatUniTest
Toolchain, a suite of seamlessly integrated tools enhancing the
capabilities of ChatUniTest. 

## Overview

![Overview](docs/img/overview.png)

### Implementations
| Publication | Implementation | Paper Titile |
| :---------: | :--: | :----------: |
| FSE'24 Demo | [maven-plugin](https://github.com/ZJU-ACES-ISE/chatunitest-maven-plugin)<br> Run with default phaseType  | [ChatUniTest: A Framework for LLM-Based Test Generation](https://dl.acm.org/doi/abs/10.1145/3663529.3663801) |
| FSE'24 | [maven-plugin](https://github.com/ZJU-ACES-ISE/chatunitest-maven-plugin)<br> Run with `CHATTESTER` phaseType | [Evaluating and Improving ChatGPT for Unit Test Generation](https://dl.acm.org/doi/abs/10.1145/3660783) |
| ICSE'24 Demo | [maven-plugin](https://github.com/ZJU-ACES-ISE/chatunitest-maven-plugin)<br> Run with `TESTSPARK` phaseType | [TestSpark: IntelliJ IDEA’s Ultimate Test Generation Companion](https://dl.acm.org/doi/abs/10.1145/3639478.3640024) |
| FSE'24 | [maven-plugin](https://github.com/ZJU-ACES-ISE/chatunitest-maven-plugin)<br> Run with `SYMPROMPT` phaseType | [Code-Aware Prompting: A study of Coverage Guided Test Generation in Regression Setting using LLM](https://dl.acm.org/doi/abs/10.1145/3643769) |
| ASE'24 | [maven-plugin](https://github.com/ZJU-ACES-ISE/chatunitest-maven-plugin)<br> Run with `HITS` phaseType | [HITS: High-coverage LLM-based Unit Test Generation via Method Slicing](https://dl.acm.org/doi/abs/10.1145/3691620.3695501) |
| IST'24 | [maven-plugin](https://github.com/ZJU-ACES-ISE/chatunitest-maven-plugin)<br> Run with `MUTAP` phaseType | [Effective Test Generation Using Pre-trained Large Language Models and Mutation Testing](https://www.sciencedirect.com/science/article/abs/pii/S0950584924000739) |
| Arxiv | [maven-plugin](https://github.com/ZJU-ACES-ISE/chatunitest-maven-plugin)<br> Run with `TELPA` phaseType | [Enhancing LLM-based Test Generation for Hard-to-Cover Branches via Program Analysis](https://arxiv.org/abs/2404.04966) |
| FSE'25 | [maven-plugin](https://github.com/ZJU-ACES-ISE/chatunitest-maven-plugin)<br> Run with `COVERUP` phaseType | [CoverUp: Coverage-Guided LLM-Based Test Generation](https://arxiv.org/abs/2403.16218) |
| TSE'23 | [maven-plugin](https://github.com/ZJU-ACES-ISE/chatunitest-maven-plugin)<br> Run with `TESTPILOT` phaseType | [An Empirical Evaluation of Using Large Language Models for Automated Unit Test Generation](https://ieeexplore.ieee.org/document/10329992) |
| ICSE'23 | CodaMOSA <br> (Under construction) | [CodaMosa: Escaping Coverage Plateaus in Test Generation with Pre-trained Large Language Models](https://ieeexplore.ieee.org/abstract/document/10172800) |


## Citation

```
@inproceedings{chen2024chatunitest,
  title={ChatUniTest: A Framework for LLM-Based Test Generation},
  author={Chen, Yinghao and Hu, Zehao and Zhi, Chen and Han, Junxiao and Deng, Shuiguang and Yin, Jianwei},
  booktitle={Companion Proceedings of the 32nd ACM International Conference on the Foundations of Software Engineering},
  pages={572--576},
  year={2024}
}
```

Please refer to the [python](https://github.com/ZJU-ACES-ISE/ChatUniTest/tree/python) branch if you want to see the original version of ChatUniTest for the paper.

```

@misc{xie2023chatunitest,
      title={ChatUniTest: a ChatGPT-based automated unit test generation tool}, 
      author={Zhuokui Xie and Yinghao Chen and Chen Zhi and Shuiguang Deng and Jianwei Yin},
      year={2023},
      eprint={2305.04764},
      archivePrefix={arXiv},
      primaryClass={cs.SE}
}
```

## :email: Contact us

If you have any questions, please feel free to contact us via email. The email addresses of the authors are as follows:

Corresponding author: `zjuzhichen AT zju.edu.cn`


## Paper list 

A curation of awesome papers about LLM for unit testing.

**2024**

- TestBench: Evaluating Class-Level Test Case Generation Capability of Large Language Models
- Retrieval-Augmented Test Generation: How Far Are We?
- Rethinking the Influence of Source Code on Test Case Generation
- Leveraging Large Language Models for Enhancing the Understandability of Generated Unit Tests
- HITS: High-coverage LLM-based Unit Test Generation via Method Slicing
- A System for Automated Unit Test Generation Using Large Language Models and Assessment of Generated Test Suites
- TestART: Improving LLM-based Unit Test via Co-evolution of Automated Generation and Repair Iteration
- An LLM-based Readability Measurement for Unit Tests' Context-aware Inputs
- Chat-like Asserts Prediction with the Support of Large Language Model
- Optimizing Search-Based Unit Test Generation with Large Language Models: An Empirical Study
- LIReDroid: LLM-Enhanced Test Case Generation for Static Sensitive Behavior Replication
- Harnessing the Power of LLMs: Automating Unit Test Generation for High-Performance Computing
- Augmenting LLMs to Repair Obsolete Test Cases with Static Collector and Neural Reranker
- Effective test generation using pre-trained Large Language Models and mutation testing
- An Empirical Study of Unit Test Generation with Large Language Models
- CasModaTest: A Cascaded and Model-agnostic Self-directed Framework for Unit Test Generation
- Enhancing LLM-based Test Generation for Hard-to-Cover Branches via Program Analysis
- CoverUp: Coverage-Guided LLM-Based Test Generation
- Enhancing Large Language Models for Text-to-Testcase Generation
- Automated Unit Test Improvement using Large Language Models at Meta
- Code-Aware Prompting: A study of Coverage Guided Test Generation in Regression Setting using LLM
- Automated Test Case Repair Using Language Models
- An Empirical Evaluation of Using Large Language Models for Automated Unit Test Generation
- Automatic Generation of Test Cases based on Bug Reports: a Feasibility Study with Large Language Models
- Using Large Language Models to Generate JUnit Tests: An Empirical Study
- ChatGPT vs SBST: A Comparative Assessment of Unit Test Suite Generation
- TestSpark: IntelliJ IDEA's Ultimate Test Generation Companion
- Towards Understanding the Effectiveness of Large Language Models on Directed Test Input Generation

**2023**

- Automatic Generation of Test Cases based on Bug Reports: a Feasibility Study with Large Language Models
- Prompting Code Interpreter to Write Better Unit Tests on Quixbugs Functions
- Automated Test Case Generation Using Code Models and Domain Adaptation
- ChatGPT vs SBST: A Comparative Assessment of Unit Test Suite Generation
- No More Manual Tests? Evaluating and Improving ChatGPT for Unit Test Generation
- CodaMosa: Escaping Coverage Plateaus in Test Generation with Pre-trained Large Language Models
- Exploring the Effectiveness of Large Language Models in Generating Unit Tests
- Adaptive Test Generation Using a Large Language Model




