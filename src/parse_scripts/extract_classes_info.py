import os
import json
import argparse
import subprocess
from ClassParser import ClassParser


def get_class_path(start_path, filename):
    for root, dirs, files in os.walk(start_path):
        if filename in files:
            return(os.path.join(root, filename))


def process_d4j_revisions(repo_path, repo_id, grammar_file, tmp, output, focal_classes_json):
    """
    Analysis defects4j revisions focal method.
    """
    if '_f' not in os.path.basename(repo_path):
        return
    os.makedirs(tmp, exist_ok=True)
    repo_out = os.path.join(output, str(repo_id))
    os.makedirs(repo_out, exist_ok=True)
    language = 'java'

    # Logging
    log_path = os.path.join(output, "log.txt")
    log = open(log_path, "w")

    #Run analysis
    print("Parser focal class...")
    project_name = os.path.split(repo_path)[1]
    with open(focal_classes_json, 'r') as f:
        content = json.load(f)
    for repo in content:
        if repo['project'] == project_name:
            classes = repo['classes']
    focals = []
    for _class in classes:
        class_path = get_class_path(repo_path, os.path.basename(_class.rstrip('\n').replace('.', '/')+'.java'))
        focals.append(class_path)

    parser = ClassParser(grammar_file, language)
    return parse_all_classes(parser, focals, project_name, repo_out, log)


def analyze_project(repo_path, repo_id, grammar_file, tmp, output):
    """
    Analyze a single project
    """
    #Create folders
    os.makedirs(tmp, exist_ok=True)
    repo_out = os.path.join(output, str(repo_id))
    os.makedirs(repo_out, exist_ok=True)
    language = 'java'
    #Run analysis
    print("Parser all class...")
    tot_m = find_classes(repo_path, grammar_file, language, repo_out)


def find_classes(root, grammar_file, language, output):
    """
    Find all classes exclude tests
    Finds test cases using @Test annotation
    """
    # Logging
    log_path = os.path.join(output, "log.txt")
    log = open(log_path, "w")

    # Move to folder
    if os.path.exists(root):
        os.chdir(root)
    else:
        return 0, 0, 0, 0

    #Test Classes
    try:
        result = subprocess.check_output(r'grep -l -r @Test --include \*.java', shell=True)
        tests = result.decode('ascii').splitlines()
    except:
        tests = []
        log.write("Error during tests" + '\n')

    #Java Files
    try:
        result = subprocess.check_output(['find', '-name', '*.java'])
        java = result.decode('ascii').splitlines()
        java = [j.replace("./", "") for j in java]
    except:
        log.write("Error during find java file" + '\n')
        return 0, 0, 0, 0

    # All Classes exclude tests
    focals = list(set(java) - set(tests))
    focals = [f for f in focals if not "src/test" in f]
    focals_norm = [f.lower() for f in focals]
    
    log.write("Java Files: " + str(len(java)) + '\n')
    log.write("Test Classes: " + str(len(tests)) + '\n')
    log.write("Potential Focal Classes: " + str(len(focals)) + '\n')
    log.flush()

    parser = ClassParser(grammar_file, language)
    project_name = os.path.split(root)[1]
    return parse_all_classes(parser, focals, project_name, output, log)

def parse_all_classes(parser, focals, project_name, output, log):
    classes = {}
    for focal in focals:
        log.write("----------" + '\n')
        log.write("Focal: " + focal + '\n')
        parsed_classes = parser.parse_file(focal)
        for _class in parsed_classes:
            _class["project_name"] = project_name

        classes[focal] = parsed_classes
        json_path = os.path.join(output, os.path.split(focal)[1] +".json")
        export(classes[focal], json_path)

        log.write("+++++++++" + '\n')
        log.write("Focal classes: " + str(len(parsed_classes)) + '\n')

    log.write("==============" + '\n')
    log.write("Files: " + str(len(focals)) + '\n')
    return classes


def export(data, out):
    """
    Exports data as json file
    """
    with open(out, "w") as text_file:
        data_json = json.dumps(data)
        text_file.write(data_json)    


def parse_args():
    """
    Parse the args passed from the command line
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo_id",
        type=str,
        default="0",
        help="ID used to refer to the repo",
    )
    parser.add_argument(
        "--repo_path",
        type=str,
        default="null",
        help="Repopath of the target repository",
    )
    parser.add_argument(
        "--grammar",
        type=str,
        default="/root/TestGPT_ASE/src/parse_scripts/java-grammar.so",
        help="Filepath of the tree-sitter grammar",
    )
    parser.add_argument(
        "--tmp",
        type=str,
        default="/root/tmp/tmp/",
        help="Path to a temporary folder used for processing",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="/root/tmp/output/",
        help="Path to the output folder",
    )

    return vars(parser.parse_args())


def main():
    args = parse_args()
    repo_path = args['repo_path']
    repo_id = args['repo_id']
    grammar_file = args['grammar']
    tmp = args['tmp']
    output = args['output']
    
    analyze_project(repo_path, repo_id, grammar_file, tmp, output)
    # process_d4j_revisions(repo_path, repo_id, grammar_file, tmp, output, '/data/share/TestGPT_ASE/src/parse_scripts/focal_classes.json')


if __name__ == '__main__':
    main()
