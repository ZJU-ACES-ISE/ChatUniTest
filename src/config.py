import configparser

# Use configparser.ConfigParser() to read config.ini file.
config = configparser.ConfigParser()
config.read("../config/config.ini")

thread_number = eval(config.get("DEFAULT", "thread_number"))
test_number = eval(config.get("DEFAULT", "test_number"))
max_rounds = eval(config.get("DEFAULT", "max_rounds"))
MAX_PROMPT_TOKENS = eval(config.get("DEFAULT", "MAX_PROMPT_TOKENS"))
MIN_ERROR_TOKENS = eval(config.get("DEFAULT", "MIN_ERROR_TOKENS"))

dataset_dir = config.get("DEFAULT", "dataset_dir")
result_dir = config.get("DEFAULT", "result_dir")
projects_dir = config.get("DEFAULT", "projects_dir")

api_keys = eval(config.get("openai", "api_keys"))
model = config.get("openai", "model")
temperature = eval(config.get("openai", "temperature"))
top_p = eval(config.get("openai", "top_p"))
frequency_penalty = eval(config.get("openai", "frequency_penalty"))
presence_penalty = eval(config.get("openai", "presence_penalty"))
