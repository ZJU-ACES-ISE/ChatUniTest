import sys
import argparse
import os
import subprocess
import re
import signal
import psutil
import time
import concurrent.futures
from run_test_case.run_test_cases import start_run, start_single_test
from parse_response import start_process
from tools import *
from config import *
from colorama import Fore, Style, init
init()

# define the threshold for CPU utilization
cpu_threshold = 80
# define the threshold for available memory
mem_threshold = 1024 * 1024 * 5000  # 5G

TIMEOUT = 30


def start_parse_test(response_src, target_dir):
    """
    Parse responses and run tests
    :param response_src: responses directory path, e.g., /data/share/TestGPT_ASE/result/scope_test%20230414210243%d3_1/
    :param target_dir: target project path
    """
    test_cases_src = start_process(response_src)
    total_compile, total_test_run = start_run(test_cases_src, target_dir)


def start_test(test_cases_src, target_dir):
    """
    Only run tests
    TODO: delete files before run
    :param test_cases_src:  tests directory path, e.g., /data/share/TestGPT_ASE/result/scope_test%20230414210243%d3_1/1460%lang_1_f%ToStringBuilder%append%d3/5
    :param target_dir: target project path
    :return Success(True) or Fail(False)
    """
    # remove_single_test_output_dirs(target_dir)

    if target_dir.endswith('_f') or target_dir.endswith('_b'):
        # defects4j project
        if check_java_version() != 11:
            raise Exception(Fore.RED + "Wrong java version! Need: java 11")
        test_case_src = os.path.join(test_cases_src, 'temp')
        run_with_d4j(test_case_src, target_dir)
    else:
        # general project
        if check_java_version() != 17:
            # TODO: uncomment this code
            # raise Exception(Fore.RED + "Wrong java version! Need: java 17")
            pass
        start_single_test(test_cases_src, target_dir)


def run_numberUtils(response_src, target_dir):
    '''
    Run NumberUtils test cases for compare.
    '''
    # test_cases_src = start_process(response_src)
    # delete cobertura.ser files before run.

    remove_single_test_output_dirs(target_dir)
    test_cases_src = response_src
    for method in os.listdir(test_cases_src):
        method_path = os.path.join(test_cases_src, method)
        if not os.path.isdir(method_path):
            continue
        for num in sorted(os.listdir(method_path)):
            try:
                tc_path = os.path.join(method_path, num)
                if start_test(tc_path, target_dir):
                    print("Success processed method: ", method, "num: ", num)
            except Exception as e:
                print(e)


def run_with_d4j(test_case_src, project_path):
    """
    Adaptive assignment for d4j tests
    :param test_case_src: /root/TestGPT_ASE/result_429/scope_test%20230428134414%/4950%Chart_8_f%Week%getYear%d1/1/temp
    """
    # loop until the CPU utilization falls below the threshold
    while True:
        # get the current CPU utilization
        cpu_utilization = psutil.cpu_percent()
        mem_available = psutil.virtual_memory().available

        # if the CPU utilization is below the threshold, start a new process and break the loop
        if cpu_utilization < cpu_threshold and mem_available > mem_threshold:
            run_d4j(test_case_src, project_path)
            break

        # if the CPU utilization is still above the threshold, wait for some time (e.g. 1 second) and check again
        time.sleep(2)


def run_d4j(test_case_src, project_path):
    '''
    Run single test using defects4j test api
    :param test_case_src: /root/TestGPT_ASE/result_429/scope_test%20230428134414%/4950%Chart_8_f%Week%getYear%d1/1/temp
    '''
    d4j_script = 'scripts/d4j_test.sh'
    process = subprocess.Popen(["bash", d4j_script, test_case_src, project_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print(result.stdout)
    stdout, stderr = process.communicate()
    start_time = time.monotonic()
    while True:
        exit_code = process.poll()
        if exit_code is not None:
            if exit_code != 0:
                with open(os.path.join(test_case_src, 'compile_error.txt'), "w") as f:
                    pattern = r"compile\.gen\.tests:(.*?)BUILD FAILED"
                    # pattern = r"    [javac] (.*?)BUILD FAILED"
                    match = re.search(pattern, stderr.decode(), re.DOTALL)
                    if match:
                        compile_output = match.group(1).strip().split('[javac] ', 1)[1]
                        compile_output = compile_output.replace('    [javac] ', '')
                        f.write(compile_output)
                    else:
                        # print("No match found")
                        f.write(stderr.decode())
            break
        elif time.monotonic() - start_time >= TIMEOUT:
            sub_pids = find_processes_created_by(process.pid)
            for pid in sub_pids:
                os.kill(pid, signal.SIGTERM)
            print("!!!!!!!!!!!!TIME OUT!!!!!!!!!!!")
            break
        else:
            time.sleep(0.1)


def run_d4j_b(tests_src, threaded=True):
    """
    run tests at defects4j buggy revisions
    :param tests_src: result directory, e.g., /root/TestGPT_ASE/result/
    """
    target_path = os.path.abspath(projects_dir)
    if threaded:
        with concurrent.futures.ProcessPoolExecutor(max_workers=thread_number) as executor:
            for scope_tests in os.listdir(tests_src):
                scope_tests_path = os.path.join(tests_src, scope_tests)
                for tests_dir in os.listdir(scope_tests_path):
                    tests_path = os.path.join(scope_tests_path, tests_dir)
                    m_id, project_name, class_name, method_name = parse_directory_name(tests_path)
                    project_path = os.path.join(target_path, project_name.replace('_f', '_b'))
                    for i in range(1, test_number + 1):
                        if not os.path.exists(os.path.join(tests_path, str(i))):
                            continue
                        print("Processing project:", project_name, "method id:", m_id, "test number:", str(i))
                        test_case_src = os.path.join(tests_path, str(i), 'temp')
                        executor.submit(run_d4j, test_case_src, project_path)
    else:
        for scope_tests in os.listdir(tests_src):
            scope_tests_path = os.path.join(tests_src, scope_tests)
            for tests_dir in os.listdir(scope_tests_path):
                tests_path = os.path.join(scope_tests_path, tests_dir)
                m_id, project_name, class_name, method_name = parse_directory_name(tests_path)
                project_path = os.path.join(target_path, project_name.replace('_f', '_b'))
                for i in range(1, test_number + 1):
                    if not os.path.exists(os.path.join(tests_path, str(i))):
                        continue
                    print("Processing project:", project_name, "method id:", m_id, "test number:", str(i))
                    test_case_src = os.path.join(tests_path, str(i), 'temp')
                    run_d4j(test_case_src, project_path)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Run test cases generated by ChatGPT")
    # parser.add_argument("response_src", help="The directory that stores all responses")
    # parser.add_argument("target_dir", help="The target directory that stores repositories or a single repositories")
    # args = parser.parse_args()
    # start_parse_test(args.response_src, args.target_dir)
    # run_numberUtils(args.response_src, args.target_dir)
    run_d4j_b('/root/TestGPT_ASE/tmp/d4j_test_b')
