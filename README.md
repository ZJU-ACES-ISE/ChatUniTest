# ChatUniTest: A ChatGPT-based unit test generation tool

ChatUniTest can automatically generate unit tests for an entire Java project in three steps.


![Alt Text](demo.gif)

## License

The project is licensed under the [MIT License](https://opensource.org/licenses/MIT).


## Step 1 : installation
First make sure you run this program in a Linux system with mysql installed.

Follow the instructions below to install the project:

1. Clone the project: `git clone https://github.com/ZJU-ACES-ISE/ChatUniTest.git`
2. Enter the project directory: `cd ChatUniTest`
3. Install the requirements: `pip install -r requirements.txt`

## Step 2: configuration

An example configuration file is provided at `config/config_example.ini`. Copy this file and rename it to `config.ini`
to ensure your data's security.

You need to alter few options:

1. `project_dir`: compiled Java project directory.
2. `api_keys`
3. `host`, `port`, `database`, `user`, `password`

The options are explained as follows:

```ini
[DEFAULT]
test_number = 6 #The number of attempts to generate for each focal method.
process_number = 32 # The number of processes to use when generating tests.
dataset_dir = ../dataset/ # Dataset directory, no need to change.
result_dir = ../result/ # Result directory, no need to change.
project_dir = ../Chart/ # compiled Java project directory.
max_rounds = 6 # The maximum number of rounds to generate one test. One round for generation, 5 rounds for repairing the test.
TIMEOUT = 30 # The timeout for each test.
MAX_PROMPT_TOKENS = 2700 # The maximum number of tokens for each prompt.
MIN_ERROR_TOKENS = 500 # The minimum number of tokens for each error prompt.
PROMPT_TEMPLATE_NO_DEPS = d1_4.jinja2 # The prompt template for the method with no dependencies.
PROMPT_TEMPLATE_DEPS = d3_4.jinja2 # The prompt template for the method with dependencies.
PROMPT_TEMPLATE_ERROR = error_3.jinja2 # The prompt template for repairing the test.

LANGUAGE = "java"
GRAMMAR_FILE = ./dependencies/java-grammar.so
COBERTURA_DIR = ./dependencies/cobertura-2.1.1
JUNIT_JAR = ./dependencies/lib/junit-platform-console-standalone-1.9.2.jar
MOCKITO_JAR = ./dependencies/lib/mockito-core-3.12.4.jar:./dependencies/lib/mockito-inline-3.12.4.jar:./dependencies/lib/mockito-junit-jupiter-3.12.4.jar:./dependencies/lib/byte-buddy-1.14.4.jar:./dependencies/lib/byte-buddy-agent-1.14.4.jar:./dependencies/lib/objenesis-3.3.jar
LOG4J_JAR = ./dependencies/lib/slf4j-api-1.7.5.jar:./dependencies/lib/slf4j-log4j12-1.7.12.jar:./dependencies/lib/log4j-1.2.17.jar
JACOCO_AGENT = ./dependencies/jacoco/jacocoagent.jar
JACOCO_CLI = ./dependencies/jacoco/jacococli.jar
REPORT_FORMAT = xml # The coverage report format.


[openai]
api_keys = [sk-xxx] # The OpenAI api keys, you can get them from https://platform.openai.com/account/api-keys
model = gpt-3.5-turbo # gpt-3.5-turbo or gpt-4
temperature = 0.5 # See https://platform.openai.com/docs/api-reference/chat/create
top_p = 1
frequency_penalty = 0
presence_penalty = 0


[database]
host = 127.0.0.1
port = 3306
database = xxxx # Database name
user = xxxx # User
password = xxxx # Password
```

## Step 3: Run

1. Enter the source code directory: `cd src`
2. Run the Python script: `python run.py`

Then, wait for the process to finish. The result is saved in the result directory.

## Structure

### config

This directory stores the config files.

The `config_example.ini` is for demonstration only. Be sure to copy it and rename it to `config.ini`.

### dataset

This directory stores the dataset. Before generating unit tests for a new project, this dataset will be deleted and
re-created automatically. So if you need the information inside the dataset directory, make sure to save a copy. The
dataset directory includes `direction_1`, `direction_3`, and `raw_data`.

1. `direction_1` contains the context without dependencies.
2. `direction_3` contains the context with dependencies.
3. `raw_data` contains all the information about focal methods.

### prompt

This directory stores the prompt templates. Prompts should be in the jinja2 template format.
If you need to add a new prompt, follow these instructions:

1. Create a user prompt template: `xxxx.jinja2`.
2. If you need to create system prompt template, the format is `xxxx_system.jinja2`, the program will automatically find
   the system prompt template.
3. Ensure you've changed the template name in the configuration file.

### result

The nested structure of the result directory is as follows:

1. scope_test + % + time + %
2. method_id + % + class_name + %d1
3. A number that denotes the different attempt, which contains all the files generated during the process, including:

    1. steps_GPT_rounds.json: Raw response from OpenAI.
    2. steps_raw_rounds.json: The raw test extracted from the raw response, and the result of the validation process.
    3. steps_imports_rounds.json: The test after import repairs, and the result of the validation process.
    4. temp: Contains the latest error message or coverage result and a test java file.

### src
This is the directory that stores the source code.

## MISC

Our work has been submitted to arXiv. Check it out here: [ChatUniTest](https://arxiv.org/abs/2305.04764).

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

## Contact us


If you have any questions or would like to inquire about our experimental results, please feel free to contact us via email. The email addresses of the authors are as follows:

1. Corresponding author: `zjuzhichen AT zju.edu.cn`
2. Author: `xiezhuokui AT zju.edu.cn`, `yh_ch AT zju.edu.cn`
