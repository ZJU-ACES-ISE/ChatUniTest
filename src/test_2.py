import os
import json

total_files = 0
total_prompt = 0
total_completion = 0

max_prompt = 0
max_completion = 0
max_file = ""


def process_json_file(file_path):
    global total_files, total_prompt, total_completion, max_prompt, max_completion, max_file
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        # Process the JSON data as needed
        total_files += 1
        total_prompt += data["usage"]["prompt_tokens"]
        total_completion += data["usage"]["completion_tokens"]
        if data["usage"]["prompt_tokens"] > max_prompt:
            max_prompt = data["usage"]["prompt_tokens"]
        if data["usage"]["completion_tokens"] > max_completion:
            max_completion = data["usage"]["completion_tokens"]
            max_file = os.path.abspath(file_path)


def find_json_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                process_json_file(file_path)


if __name__ == "__main__":
    directory = "../result/"
    find_json_files(directory)
    print("Total files: ", total_files)
    print("Total prompt tokens: ", total_prompt)
    print("Total completion tokens: ", total_completion)
    print("Average prompt tokens: ", total_prompt / total_files)
    print("Average completion tokens: ", total_completion / total_files)
    print("Average per file: ", (total_prompt + total_completion) / total_files)
    print("Max prompt tokens: ", max_prompt)
    print("Max completion tokens: ", max_completion)
    print("Max file: ", max_file)
