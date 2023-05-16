import json
import os


def print_answer(file_path):
    # Read in data
    with open(file_path, "r") as f:
        data = json.load(f)
    info = file_path.split("/")[-1].split("_")
    print("project_name: " + info[1], "class_name: " + info[2], "method_name: " + info[3], "direction: " + info[4],
          "test_number: " + info[5])
    # Print answer
    print(data["choices"][0]["message"]["content"])


def walk_over_directory(directory):
    # Walk over directory
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".json"):
                print_answer(os.path.join(root, filename))
                while input("Next answer? (y/n): ") != "y":
                    pass


if __name__ == '__main__':
    directory = "../result/scope_test_20230409185306_d1"
    walk_over_directory(directory)
