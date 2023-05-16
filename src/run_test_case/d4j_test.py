import os
import sys
import subprocess
from pathlib import Path


def prepare_test_suite(test_suite, tar_suite_name, WD):
    os.chdir(WD)
    java_files = list(Path(test_suite).rglob("*.java"))
    for java_file in java_files:
        process_single_test(str(java_file))
    subprocess.run(["tar", "cvjf", tar_suite_name, PACKAGE_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Prepare test suite finished")

def process_single_test(class_file):
    os.chdir(WD)
    with open(class_file, "r") as f:
        PACKAGE_PATH = ''.join([x for x in f.readlines() if x.startswith('package')])
        PACKAGE_PATH = PACKAGE_PATH.replace('package', '').replace(';', '').replace('.', '/').strip()
    if PACKAGE_PATH:
        os.makedirs(PACKAGE_PATH, exist_ok=True)
        subprocess.run(["cp", "-r", class_file, PACKAGE_PATH])

def run_test():
    os.chdir(project_path)
    remove_files()
    cmd = ["defects4j", "coverage", "-s", f"{WD}/{tar_suite_name}"]
    if instrument_class:
        cmd.extend(["-i", instrument_class])
    subprocess.run(cmd)
    get_results()
    os.chdir(WD)

def get_results():
    if os.path.isfile(f"{project_path}/failing_tests"):
        subprocess.run(["cp", f"{project_path}/failing_tests", f"{test_suite}/runtime_error.txt"])
        return
    if os.path.isfile(f"{project_path}/coverage.xml"):
        subprocess.run(["cp", f"{project_path}/coverage.xml", test_suite])
        subprocess.run(["cp", f"{project_path}/summary.csv", test_suite])
        subprocess.run(["cp", f"{project_path}/all_tests", test_suite])

def remove_files():
    files = ["summary.csv", "all_tests", "failing_tests", "coverage.xml"]
    for file in files:
        if os.path.isfile(file):
            os.remove(file)

def clean_wd():
    print("Cleaning working directory...")
    if os.path.exists(WD):
        shutil.rmtree(WD)

def run_d4j_test(test_suite, project_path):
    project_name = os.path.basename(project_path)
    test_num = Path(test_suite).parts[-2]
    method_name = Path(test_suite).parts[-3]
    tar_suite_name = f"{project_name}_{method_name}.{test_num}.tar.bz2"
    WD = f"/data/share/TestGPT_ASE/src/scripts/tmp/{method_name}/{test_num}"
    javapath = "/data/chenyi/jvm/jdk1.8.0_202"
    if not os.path.exists(WD):
        os.makedirs(WD)

    if os.environ["JAVA_HOME"] != javapath:
        print(f"JAVA_HOME should be set to {javapath} !!!")
        sys.exit(1)

    prepare_test_suite(test_suite, tar_suite_name, WD)
    run_test()
    clean_wd()


if __name__ == "__main__":
    test_suite = sys.argv[1]
    project_path = sys.argv[2]
    instrument_class = sys.argv[3] if len(sys.argv) > 3 else None

    run_d4j_test(test_suite, project_path)

