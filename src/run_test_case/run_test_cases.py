import json
import glob
import os
import subprocess
import re
from datetime import datetime
from run_test_case.copy_tests import copy_tests
from run_test_case.make_dependency import make_dependency
import argparse

# Dependencies
COBERTURA_DIR = "./run_test_case/dependencies/cobertura-2.1.1"
JUNIT_JAR = "./run_test_case/dependencies/lib/junit-platform-console-standalone-1.9.2.jar"
MOCKITO_JAR = "./run_test_case/dependencies/lib/mockito-core-3.12.4.jar:\
./run_test_case/dependencies/lib/mockito-inline-3.12.4.jar:\
./run_test_case/dependencies/lib/mockito-junit-jupiter-3.12.4.jar:\
./run_test_case/dependencies/lib/byte-buddy-1.14.4.jar:\
./run_test_case/dependencies/lib/byte-buddy-agent-1.14.4.jar:\
./run_test_case/dependencies/lib/objenesis-3.3.jar"
LOG4J_JAR = "./run_test_case/dependencies/lib/slf4j-api-1.7.5.jar:\
./run_test_case/dependencies/lib/slf4j-log4j12-1.7.12.jar:\
./run_test_case/dependencies/lib/log4j-1.2.17.jar"

REPORT_FORMAT = 'xml'

COMPILE_ERROR = 0
TEST_RUN_ERROR = 0
TEST_NUMBER = 6
TIMEOUT = 30


def cAdd(test_file):
    global COMPILE_ERROR
    project = os.path.basename(os.getcwd())
    # print("COMPILE ERROR: [", project, "] : [", test_file, "]")
    COMPILE_ERROR += 1


def tAdd(full_test_name):
    global TEST_RUN_ERROR
    project = os.path.basename(os.getcwd())
    # print("TESTS FAILED: [", project, "] : [", full_test_name, "]")
    TEST_RUN_ERROR += 1


def instrument(project_path, instrument_dir, datafile_dir):
    """
    Use cobertura scripts to instrument compiled class.
    Generate 'instrumented' directory.
    """
    if not os.path.exists(instrument_dir):
        os.mkdir(instrument_dir)
    if not os.path.exists(datafile_dir):
        os.mkdir(datafile_dir)
    # print("Instrumenting ", os.path.basename(project_path), instrument_dir, datafile_dir)
    if 'instrumented' in os.listdir(instrument_dir):
        return


    if has_submodule(project_path):
        target_classes = os.path.join(project_path, '**/target/classes')
    else:
        target_classes = os.path.join(project_path, 'target/classes')

    result = subprocess.run(["bash", os.path.join(COBERTURA_DIR, "cobertura-instrument.sh"),
                             "--basedir", project_path,
                             "--destination", f"{instrument_dir}/instrumented",
                             "--datafile", f"{datafile_dir}/cobertura.ser",
                             target_classes], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def get_test_name(test_case):
    return os.path.basename(test_case)


def export_classpath(classpath_file, classpath):
    with open(classpath_file, 'w') as f:
        classpath = "-cp " + classpath
        f.write(classpath)
    return


def compile_test(test_case, dependencies, test_cases_dir, build_dir, compiled_tests_dir, compiler_output):
    """
    Compile a test case.
    :param test_case:
    :param dependencies:
    :param test_cases_dir: the directory stores testcase.java
    :param build_dir: src class build directory
    :param compiled_tests_dir: the directory to store compiled tests
    :param compiler_output:
    """

    test_name = get_test_name(test_case)
    if os.path.basename(compiler_output) == 'compile_error':
        compiler_output_file = f"{compiler_output}.txt"
    else:
        compiler_output_file = f"{compiler_output}-{test_name}.txt"
    test_file = os.path.join(test_cases_dir, f"{test_case}.java")

    if not os.path.exists(compiled_tests_dir):
        os.mkdir(compiled_tests_dir)

    classpath = f"{dependencies}:{JUNIT_JAR}:{MOCKITO_JAR}:{LOG4J_JAR}:{build_dir}:."
    classpath_file = os.path.join(compiled_tests_dir, 'classpath.txt')
    export_classpath(classpath_file, classpath)

    # result = subprocess.run(["javac", "-d", compiled_tests_dir, "-cp", classpath, test_file],
    #                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result = subprocess.run(["javac", "-d", compiled_tests_dir, f"@{classpath_file}", test_file],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        cAdd(test_file)
        with open(compiler_output_file, "w") as f:
            f.write(result.stdout)
            f.write(result.stderr)
        return False
    return True


def get_package(test_file):
    with open(test_file, "r") as f:
        first_line = f.readline()

    package = first_line.strip().replace("package ", "").replace(";", "")
    return package


def report(datafile_dir, report_dir):
    # print("Reporting...", datafile_dir, report_dir)
    if not os.path.exists(report_dir):
        os.mkdir(report_dir)

    result = subprocess.run(["bash", os.path.join(COBERTURA_DIR, "cobertura-report.sh"),
                             "--format", REPORT_FORMAT, "--datafile", f"{datafile_dir}/cobertura.ser", "--destination",
                             report_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def is_module(project_path):
    """
    If the path has a pom.xml file and target/classes compiled, a module.
    """
    if not os.path.isdir(project_path):
        return False
    if 'pom.xml' in os.listdir(project_path) and 'target' in os.listdir(project_path):
        return True
    return False


def get_submodule(project_path):
    """
    Get all modules in given project.
    :return: module list
    """
    return [d for d in os.listdir(project_path) if is_module(os.path.join(project_path, d))]


def has_submodule(project_path):
    """
    Is a project composed by submodules, e.g., gson
    """
    for dir in os.listdir(project_path):
        if is_module(os.path.join(project_path, dir)):
            return True
    return False


def run_single_test(tests, test_case_file, dependencies, build_dir, compiled_tests_dir, compiler_output, test_output,
                    report_dir):
    """
    Run a test case.
    :param tests: dir to store test cases
    :param test_case_file: the test_case.java file
    :return: Whether it is successful or no.
    """
    if not test_case_file.endswith(".java"):
        return False
    test_case = os.path.splitext(test_case_file)[0]

    if not compile_test(test_case, dependencies, tests, build_dir, compiled_tests_dir, compiler_output):
        return False
    test_file = os.path.join(tests, f"{test_case}.java")
    package = get_package(test_file)
    if package != '':
        full_test_name = f"{package}.{test_case}"
    else:
        full_test_name = test_case

    if os.path.basename(test_output) == 'runtime_error':
        test_output_file = f"{test_output}.txt"
    else:
        test_output_file = f"{test_output}-{os.path.basename(test_case)}.txt"
    classpath = f"{COBERTURA_DIR}/cobertura-2.1.1.jar:{compiled_tests_dir}/instrumented:{compiled_tests_dir}:" \
                f"{dependencies}:{JUNIT_JAR}:{MOCKITO_JAR}:{LOG4J_JAR}:{build_dir}:."
    classpath_file = os.path.join(compiled_tests_dir, 'classpath.txt')
    export_classpath(classpath_file, classpath)

    try:
        # result = subprocess.run(
        #     ["java", "-cp", classpath, f"-Dnet.sourceforge.cobertura.datafile={compiled_tests_dir}/cobertura.ser",
        #      "org.junit.platform.console.ConsoleLauncher", "--disable-banner", "--disable-ansi-colors",
        #      "--fail-if-no-tests", "--details=none", "--select-class", full_test_name], timeout=TIMEOUT,
        result = subprocess.run(
            ["java", f"@{classpath_file}", f"-Dnet.sourceforge.cobertura.datafile={compiled_tests_dir}/cobertura.ser",
             "org.junit.platform.console.ConsoleLauncher", "--disable-banner", "--disable-ansi-colors",
             "--fail-if-no-tests", "--details=none", "--select-class", full_test_name], timeout=TIMEOUT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            tAdd(full_test_name)
            with open(test_output_file, "w") as f:
                f.write(result.stdout)
                error_msg = result.stderr
                error_msg = re.sub(r'log4j:WARN.*\n?', '', error_msg)
                if error_msg != '':
                    f.write(error_msg)
            return False
    except subprocess.TimeoutExpired:
        print("Timed out! ", full_test_name)
        return False
    return True


# 6 attempts test
def run_all_tests(project_path, tests_dir, build_dir, compiled_tests_dir, compiler_output, test_output, report_dir):
    """
    Run all test cases in a project.
    """
    # compiled_tests_dir = os.path.join(tests_dir, compiled_tests_dir)
    tests = os.path.join(tests_dir, "test_cases")
    # os.chdir(project_path)
    if not os.path.isdir(tests):
        return 0, 0
    # wd = os.getcwd()
    try:
        dependencies = make_dependency(project_path)
        instrument(project_path, compiled_tests_dir, compiled_tests_dir)
    except Exception as e:
        print(e)

    total_compile = 0
    for t in range(1, 1 + TEST_NUMBER):
        print("Processing attempt: ", str(t))
        for test_case_file in os.listdir(tests):
            if str(t) != test_case_file.split('_')[-1].replace('Test.java', ''):
                continue
            total_compile += 1
            try:
                run_single_test(tests, test_case_file, dependencies, build_dir, compiled_tests_dir,
                                compiler_output, test_output, report_dir)
            except Exception as e:
                print(e)

        report(compiled_tests_dir, os.path.join(report_dir, str(t)))
        total_test_run = total_compile - COMPILE_ERROR
        print("COMPILE TOTAL COUNT:", total_compile)
        print("COMPILE ERROR COUNT:", COMPILE_ERROR)
        print("TEST RUN TOTAL COUNT:", total_test_run)
        print("TEST RUN ERROR COUNT:", TEST_RUN_ERROR)
        print("\n")
    # process_report(report_dir)
    return total_compile, total_test_run


def process_run_all_repos(target_dir, test_cases_src, tests_dir, build_dir, compiled_tests_dir,
                          compiler_output, test_output, report_dir):
    total_compile = 0
    total_test_run = 0
    for project in os.listdir(target_dir):
        project_path = os.path.join(target_dir, project)
        copy_tests(test_cases_src, target_dir, tests_dir)
        build_dir = process_single_repo(project_path, build_dir)
        n1, n2 = run_all_tests(target_dir, tests_dir, build_dir, compiled_tests_dir, compiler_output,
                               test_output, report_dir)
        total_compile += n1
        total_test_run += n2

    return total_compile, total_test_run


def process_single_repo(target_dir, build_dir):
    if has_submodule(target_dir):
        modules = get_submodule(target_dir)
        postfixed_modules = [f'{target_dir}/{module}/{build_dir}' for module in modules]
        build_dir = ':'.join(postfixed_modules)
    else:
        build_dir = os.path.join(target_dir, build_dir)
    return build_dir


def parse_test_case_info(test_case_path):
    """
    Extract information of the test case path.
    """
    method_id, project_name, class_name, method_name, direction = test_case_path.rstrip('/').split('/')[-2].split('%')
    attempt_num = test_case_path.rstrip('/')[-1]
    return method_id, project_name, class_name, method_name, direction, attempt_num


def start_run(test_cases_src, target_dir):
    """
    Initialize configurations and run all tests
    :param test_cases_src: test cases directory path, e.g., /data/share/TestGPT_ASE/result/scope_test%20230414210243%d3_1/
    :param target_dir: target project path
    """
    date = datetime.now().strftime("%Y%m%d%H%M%S")
    # Directories for the test cases, outputs, and reports
    tests_dir = os.path.join(target_dir, f"tests%{date}")
    compiler_output_dir = os.path.join(tests_dir, "compiler_output")
    test_output_dir = os.path.join(tests_dir, "test_output")
    report_dir = os.path.join(tests_dir, "report")

    compiler_output = os.path.join(compiler_output_dir, "CompilerOutput")
    test_output = os.path.join(test_output_dir, "TestOutput")
    compiled_tests_dir = os.path.join(tests_dir, "tests_ChatGPT")
    build_dir = process_single_repo(target_dir, "target/classes")

    # return process_run_all_repos(target_dir, test_cases_src, tests_dir,
    #                          build_dir, compiled_tests_dir, compiler_output, test_output, report_dir)

    # run single repo test
    copy_tests(test_cases_src, target_dir, tests_dir)
    return run_all_tests(target_dir, tests_dir, build_dir, compiled_tests_dir, compiler_output,
                         test_output, report_dir)


def start_single_test(test_case_src, target_dir):
    """
    Run a single method test case with a thread.
    :param test_cases_src:  tests directory path, e.g., /data/share/TestGPT_ASE/result/scope_test%20230414210243%d3_1/1460%lang_1_f%ToStringBuilder%append%d3/5
    """
    # date = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    temp_dir = os.path.join(test_case_src, 'temp')
    method_id, project_name, class_name, method_name, direction, attempt_num = parse_test_case_info(test_case_src)
    # compiled_tests_dir = os.path.join(target_dir, f"test_{method_id}")
    compiled_tests_dir = os.path.join(test_case_src, "runtemp")
    if not os.path.exists(compiled_tests_dir):
        os.mkdir(compiled_tests_dir)
    try:
        dependencies = make_dependency(target_dir)
        instrument(target_dir, compiled_tests_dir, compiled_tests_dir)
    except Exception as e:
        print(e)
        return False
    try:
        build_dir = process_single_repo(target_dir, "target/classes")
        test_case = os.path.basename(glob.glob(temp_dir + '/*.java')[0])
        if not run_single_test(temp_dir, test_case, dependencies, build_dir,
                               compiled_tests_dir, os.path.join(temp_dir, 'compile_error'),
                               os.path.join(temp_dir, 'runtime_error'), temp_dir):
            return False
        else:
            report(compiled_tests_dir, temp_dir)
    except Exception as e:
        print(e)
        return False
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run test cases generated by ChatGPT")
    parser.add_argument("test_cases_src", help="The directory that stores all test cases")
    parser.add_argument("target_dir", help="The target directory that stores repositories or a single repositories")
    args = parser.parse_args()
    total_compile, total_test_run = start_run(args.test_cases_src, args.target_dir)
