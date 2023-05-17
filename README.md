# ChatUniTest: A ChatGPT-based unit test generation tool

This is the implementation of the tool [ChatUniTest](https://arxiv.org/abs/2305.04764).

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

![Alt Text](demo.gif)

## License

The project is licensed under the [MIT License](https://opensource.org/licenses/MIT).


## Installation

To install the project, you can follow the instructions down blow.

## Structure

### config

This is the directory to store the config files. File extension should be ".ini".

### dataset

This is the directory to store the dataset. Including direction_1, direction_2, direction_3.

### prompt

This is the directory to store the prompt templates. Prompts should be jinja2 template.

### result

This is the directory to store the answers from OpenAI.

### src

This is the directory to store the source code.
