import subprocess
import signal
import time
import concurrent.futures
from test_runner import TestRunner
from class_parser import ClassParser
from tools import *
from config import *
from colorama import Fore, init


class Task:

    @staticmethod
    def test(test_path, target_path):
        """
        Run test task, make sure the target project has be compiled and installed.(run `mvn compile install`)
        """
        test_task = TestTask(test_path, target_path)
        return test_task.single_test()

    @staticmethod
    def all_test(test_path, target_path):
        """
        Run test task, make sure the target project has be compiled and installed.(run `mvn compile install`)
        """
        test_task = TestTask(test_path, target_path)
        return test_task.all_test()

    @staticmethod
    def parse(target_path):
        """
        Run parse task, extract class information of target project.
        """
        parse_task = ParseTask()
        return parse_task.parse_project(target_path)


class TestTask:

    def __init__(self, test_path, target_path):
        init()  # colorama init
        self.test_path = test_path
        self.target_path = target_path
        self.runner = TestRunner(test_path, target_path)

        # define the threshold for CPU utilization and available memory
        self.cpu_threshold = 80
        self.mem_threshold = 1024 * 1024 * 5000  # 5G

    def single_test(self):
        """
        Only run tests.
        tests directory path, e.g., /data/share/TestGPT_ASE/result/scope_test%20230414210243%d3_1/1460%lang_1_f%ToStringBuilder%append%d3/5
        """
        if check_java_version() != 11:
            raise Exception(Fore.RED + "Wrong java version! Need: java 11")
        if self.target_path.endswith("_f") or self.target_path.endswith("_b"):  # defects4j project
            return self.start_d4j()
        else:  # general project
            return self.runner.start_single_test()

    def all_test(self):
        """
        Run all test cases.
        test_path: test cases directory path, e.g., /data/share/TestGPT_ASE/result/scope_test%20230414210243%d3_1/
        target_path: target project path
        """
        if check_java_version() != 11:
            raise Exception(Fore.RED + "Wrong java version! Need: java 11")
        return self.runner.start_all_test()

    def start_d4j(self):
        """
        Adaptive assignment for d4j tests.
        test case path: /root/TestGPT_ASE/result_429/scope_test%20230428134414%/4950%Chart_8_f%Week%getYear%d1/1/temp
        """
        # loop until the CPU utilization falls below the threshold
        while True:
            # get the current CPU utilization
            cpu_utilization = psutil.cpu_percent()
            mem_available = psutil.virtual_memory().available
            # if the CPU utilization is below the threshold, start a new process and break the loop
            if cpu_utilization < self.cpu_threshold and mem_available > self.mem_threshold:
                self.run_d4j()
                break
            # if the CPU utilization is still above the threshold, wait for some time (e.g. 1 second) and check again
            time.sleep(2)

    def run_d4j(self):
        """
        Run single test using defects4j test api
        test case path: /root/TestGPT_ASE/result_429/scope_test%20230428134414%/4950%Chart_8_f%Week%getYear%d1/1/temp
        """
        d4j_script = 'scripts/d4j_test.sh'
        test_case_src = os.path.join(self.test_path, "temp")

        process = subprocess.Popen(["bash", d4j_script, test_case_src, self.target_path], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        start_time = time.monotonic()
        while True:
            exit_code = process.poll()
            if exit_code is not None:
                if exit_code != 0:
                    with open(os.path.join(test_case_src, 'compile_error.txt'), "w") as f:
                        pattern = r"compile\.gen\.tests:(.*?)BUILD FAILED"
                        match = re.search(pattern, stderr.decode(), re.DOTALL)
                        if match:
                            compile_output = match.group(1).strip().split('[javac] ', 1)[1]
                            compile_output = compile_output.replace('    [javac] ', '')
                            f.write(compile_output)
                        else:
                            f.write(stderr.decode())
                break
            elif time.monotonic() - start_time >= TIMEOUT:
                sub_pids = find_processes_created_by(process.pid)
                for pid in sub_pids:
                    os.kill(pid, signal.SIGTERM)
                break
            else:
                time.sleep(0.1)

    def run_d4j_b(self, tests_src, threaded=True):
        """
        run tests at defects4j buggy revisions
        :param tests_src: result directory, e.g., /root/TestGPT_ASE/result/
        """
        target_path = '/root/TestGPT_ASE/projects'
        if threaded:
            with concurrent.futures.ProcessPoolExecutor(max_workers=process_number) as executor:
                for scope_tests in os.listdir(tests_src):
                    scope_tests_path = os.path.join(tests_src, scope_tests)
                    for tests_dir in os.listdir(scope_tests_path):
                        tests_path = os.path.join(scope_tests_path, tests_dir)
                        m_id, project_name, class_name, method_name = parse_file_name(tests_path)
                        project_path = os.path.join(target_path, project_name.replace('_f', '_b'))
                        self.target_path = project_path
                        for i in range(1, test_number + 1):
                            if not os.path.exists(os.path.join(tests_path, str(i))):
                                continue
                            print("Processing project:", project_name, "method id:", m_id, "test number:", str(i))
                            test_case_src = os.path.join(tests_path, str(i), 'temp')
                            self.test_path = test_case_src
                            executor.submit(self.run_d4j)
        else:
            for scope_tests in os.listdir(tests_src):
                scope_tests_path = os.path.join(tests_src, scope_tests)
                for tests_dir in os.listdir(scope_tests_path):
                    tests_path = os.path.join(scope_tests_path, tests_dir)
                    m_id, project_name, class_name, method_name = parse_file_name(tests_path)
                    project_path = os.path.join(target_path, project_name.replace('_f', '_b'))
                    self.target_path = project_path
                    for i in range(1, test_number + 1):
                        if not os.path.exists(os.path.join(tests_path, str(i))):
                            continue
                        print("Processing project:", project_name, "method id:", m_id, "test number:", str(i))
                        test_case_src = os.path.join(tests_path, str(i), 'temp')
                        self.test_path = test_case_src
                        self.run_d4j()


class ParseTask:

    def __init__(self):
        self.parser = ClassParser(GRAMMAR_FILE, LANGUAGE)
        self.output = "../class_info/"

    def parse_project(self, target_path):
        """
        Analyze a single project
        """
        # Create folders
        target_path = target_path.rstrip('/')
        os.makedirs(self.output, exist_ok=True)
        if target_path.endswith("_f") or target_path.endswith("_b"):
            _, output_path = self.process_d4j_revisions(target_path, './scripts/focal_classes.json')
            return output_path
        tot_m, output_path = self.find_classes(target_path)
        return output_path

    def find_classes(self, target_path):
        """
        Find all classes exclude tests
        Finds test cases using @Test annotation
        """
        # Run analysis
        print("Parse", target_path, " ...")
        if not os.path.exists(target_path):
            return 0, ""
        # Test Classes
        try:
            result = subprocess.check_output(r'grep -l -r @Test --include \*.java {}'.format(target_path), shell=True)
            tests = result.decode('ascii').splitlines()
        except:
            tests = []
        # Java Files
        try:
            result = subprocess.check_output(['find', target_path, '-name', '*.java'])
            java = result.decode('ascii').splitlines()
        except:
            return 0, ""
        # All Classes exclude tests
        focals = list(set(java) - set(tests))
        focals = [f for f in focals if not "src/test" in f]
        project_name = os.path.split(target_path)[1]
        output = os.path.join(self.output, project_name)
        os.makedirs(output, exist_ok=True)
        return self.parse_all_classes(focals, project_name, output), output

    def parse_all_classes(self, focals, project_name, output):
        classes = {}
        for focal in focals:
            parsed_classes = self.parser.parse_file(focal)
            for _class in parsed_classes:
                _class["project_name"] = project_name

            classes[focal] = parsed_classes
            json_path = os.path.join(output, os.path.split(focal)[1] + ".json")
            self.export_result(classes[focal], json_path)
        return classes

    @staticmethod
    def export_result(data, out):
        """
        Exports data as json file
        """
        directory = os.path.dirname(out)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(out, "w") as text_file:
            data_json = json.dumps(data)
            text_file.write(data_json)

    def get_class_path(self, start_path, filename):
        for root, dirs, files in os.walk(start_path):
            if filename in files:
                return os.path.join(root, filename)

    def process_d4j_revisions(self, repo_path, focal_classes_json):
        """
        Analysis defects4j revisions focal method.
        """
        if '_f' not in os.path.basename(repo_path):
            return
        # Run analysis
        print("Parsing focal class...")
        project_name = os.path.split(repo_path)[1]
        with open(focal_classes_json, 'r') as f:
            content = json.load(f)
        for repo in content:
            if repo['project'] == project_name:
                classes = repo['classes']
        focals = []
        for _class in classes:
            class_path = self.get_class_path(repo_path, os.path.basename(_class.rstrip('\n').replace('.', '/') + '.java'))
            focals.append(class_path)

        output = os.path.join(self.output, project_name)
        return self.parse_all_classes(focals, project_name, output), output
