import configparser

# Use configparser.ConfigParser() to read config.ini file.
config = configparser.ConfigParser()
config.read("../config/config.ini")

process_number = eval(config.get("DEFAULT", "process_number"))
test_number = eval(config.get("DEFAULT", "test_number"))
max_rounds = eval(config.get("DEFAULT", "max_rounds"))
MAX_PROMPT_TOKENS = eval(config.get("DEFAULT", "MAX_PROMPT_TOKENS"))
MIN_ERROR_TOKENS = eval(config.get("DEFAULT", "MIN_ERROR_TOKENS"))
TIMEOUT = eval(config.get("DEFAULT", "TIMEOUT"))

TEMPLATE_NO_DEPS = config.get("DEFAULT", "PROMPT_TEMPLATE_NO_DEPS")
TEMPLATE_WITH_DEPS = config.get("DEFAULT", "PROMPT_TEMPLATE_DEPS")
TEMPLATE_ERROR = config.get("DEFAULT", "PROMPT_TEMPLATE_ERROR")

LANGUAGE = config.get("DEFAULT", "LANGUAGE")
GRAMMAR_FILE = config.get("DEFAULT", "GRAMMAR_FILE")
COBERTURA_DIR = config.get("DEFAULT", "COBERTURA_DIR")
JUNIT_JAR = config.get("DEFAULT", "JUNIT_JAR")
MOCKITO_JAR = config.get("DEFAULT", "MOCKITO_JAR")
LOG4J_JAR = config.get("DEFAULT", "LOG4J_JAR")
JACOCO_AGENT = config.get("DEFAULT", "JACOCO_AGENT")
JACOCO_CLI = config.get("DEFAULT", "JACOCO_CLI")
REPORT_FORMAT = config.get("DEFAULT", "REPORT_FORMAT")

dataset_dir = config.get("DEFAULT", "dataset_dir")
result_dir = config.get("DEFAULT", "result_dir")
project_dir = config.get("DEFAULT", "project_dir")

api_keys = eval(config.get("openai", "api_keys"))
model = config.get("openai", "model")
temperature = eval(config.get("openai", "temperature"))
top_p = eval(config.get("openai", "top_p"))
frequency_penalty = eval(config.get("openai", "frequency_penalty"))
presence_penalty = eval(config.get("openai", "presence_penalty"))
