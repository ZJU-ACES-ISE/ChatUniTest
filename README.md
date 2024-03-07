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
| Arxiv | [ChatUniTest](https://github.com/ZJU-ACES-ISE/ChatUniTest/tree/python)<br>[maven-plugin](https://github.com/ZJU-ACES-ISE/ChatUniTest_IDEA_Plugin)<br>[IDEA-plugin](https://github.com/ZJU-ACES-ISE/ChatUniTest_IDEA_Plugin)  | [ChatUniTest: a ChatGPT-based automated unit test generation tool](https://arxiv.org/abs/2305.04764), by Zhuokui Xie. |
| Arxiv | [ChatTester](https://github.com/ZJU-ACES-ISE/ChatTester) | [No More Manual Tests? Evaluating and Improving ChatGPT for Unit Test Generation](https://arxiv.org/pdf/2305.04207.pdf), by Zhiqiang Yuan. |


## MISC

Our work has been submitted to arXiv. Check it out here: [ChatUniTest](https://arxiv.org/abs/2305.04764).

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

1. Corresponding author: `zjuzhichen AT zju.edu.cn`
2. Author: `yh_ch AT zju.edu.cn`, `xiezhuokui AT zju.edu.cn`
