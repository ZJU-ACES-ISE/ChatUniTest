"""
This script is for making a full-qualified name class list for each project.
Only need to run once for each DataSet.
"""
import os
import json
from pathlib import Path

def make_class_list(REPO_PATH, CLASS_LIST):
    class_list = {}
    # Iterate through directories in REPO_PATH
    for repo in os.listdir(REPO_PATH):
        repo_path = os.path.join(REPO_PATH, repo)
        if os.path.isdir(repo_path):
            repo_name = os.path.basename(repo_path)
            print(repo_name)

            # Find src/main/java directories
            tmp_dirs = [str(path) for path in Path(repo_path).rglob('*src/main/java') if path.is_dir()]

            class_list[repo_name] = []
            for tmp_dir in tmp_dirs:
                print(tmp_dir)
                java_files = [str(path) for path in Path(tmp_dir).rglob('*.java') if path.is_file()]

                # Add java files to class_list
                for file in java_files:
                    class_list[repo_name].append(file[file.find('/src/main/java/') + len('/src/main/java/'):]
                                                 .replace('/', '.').replace('.java', ''))

    # Export class_list as JSON
    with open(CLASS_LIST, 'w') as class_list_file:
        json.dump(class_list, class_list_file, indent=2)

if __name__ == "__main__":
    REPO_PATH = "/data/share/testGPT_dataset_src/"
    CLASS_LIST = "class_list.json"
    make_class_list(REPO_PATH, CLASS_LIST)
