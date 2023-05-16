import json
import os.path

import openai
from config import config
import random
import threading
import concurrent.futures
import queue
import jinja2

openai.api_key = random.choice(config.get("openai", "api_keys"))
model = config.get("openai", "model")
temperature = config.get("openai", "temperature")
top_p = config.get("openai", "top_p")
frequency_penalty = config.get("openai", "frequency_penalty")
presence_penalty = config.get("openai", "presence_penalty")
thread_number = int(config.get("DEFAULT", "thread_number"))

# Create a jinja2 environment
env = jinja2.Environment(loader=jinja2.FileSystemLoader('../../../prompt'))


def ask_chatgpt_thread(idx, messages, save_path):
    """
    Threaded version of ask_chatgpt
    :return: [{"role":"user","content":"..."}]
    """
    print(idx, "Started...")
    # Send a request to OpenAI
    completion = openai.ChatCompletion.create(messages=messages,
                                              model=model,
                                              temperature=temperature,
                                              top_p=top_p,
                                              frequency_penalty=frequency_penalty,
                                              presence_penalty=presence_penalty)
    with open(save_path, "a") as f:
        json.dump(completion, f)
    print(idx, "Finished!")
    return completion


def ask_chatgpt(messages):
    """
    Single thread ask chatgpt.
    :param messages: [{"role":"user","content":"..."}]
    :return:
    """
    completion = openai.ChatCompletion.create(messages=messages,
                                              model=model,
                                              temperature=temperature,
                                              top_p=top_p,
                                              frequency_penalty=frequency_penalty,
                                              presence_penalty=presence_penalty)
    return completion


def generate_prompt(template_name, context: dict):
    """
    Generate prompt via jinja2 engine
    :param template_name:
    :param context:
    :return:
    """
    # Load template
    template = env.get_template(template_name)
    prompt = template.render(context[0])

    return prompt


def generate_messages(template_name, file_path: str):
    """
    You can modify this function or create new function to add more information
    :param template_name:
    :param file_path:
    :return:
    """
    with open(file_path, "r") as f:
        context = json.load(f)
    messages = []
    content = generate_prompt(template_name, context)
    messages.append({"role": "user", "content": content})

    return messages


def start_generation(dataset_dir, template_name, result_dir):
    if not os.path.exists(dataset_dir):
        raise RuntimeError("Dataset path not found!")
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    # Get a list of all file paths
    file_paths = [os.path.join(dataset_dir, filename) for filename in os.listdir(dataset_dir)]

    # Create a thread pool with maximum of thread_number
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_number) as executor:
        for idx, file_path in enumerate(file_paths):
            messages = generate_messages(template_name, file_path)
            save_path = os.path.join(result_dir, os.path.basename(file_path))
            if os.path.exists(save_path):
                print(file_path, "Already exist. Skipped!")
                continue
            executor.submit(ask_chatgpt_thread, idx, messages, save_path)
    print("Main thread executing!")


if __name__ == '__main__':
    dataset_directory = '/data/share/testGPT_dataset_parsed/commons-cli/0'
    result_directory = '/data/chenyi/tmp/output'
    template_file = 'd1_1.jinja2'
    print("Dataset directory:", dataset_directory)
    print("Result directory:", result_directory)
    confirm = input("Are you sure to continue? (y/n) ")
    if confirm == "y":
        start_generation(dataset_directory, template_file, result_directory)
        print("Finished!")
    else:
        print("Canceled!")
