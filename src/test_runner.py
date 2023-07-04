import glob
import os
import subprocess
import re
from datetime import datetime
from config import *


class TestRunner:

    def __init__(self, test_path, target_path, tool="cobertura"):
        """
        :param tool: coverage tool (Only support cobertura or jacoco)
        :param test_path: test cases directory path e.g.:
        /data/share/TestGPT_ASE/result/scope_test%20230414210243%d3_1/ (all test)
        /data/share/TestGPT_ASE/result/scope_test%20230414210243%d3_1/1460%lang_1_f%ToStringBuilder%append%d3/5 (single test)
        :param target_path: target project path
        """
        self.coverage_tool = tool
        self.test_path = test_path
        self.target_path = target_path

        # Preprocess
        self.dependencies = self.make_dependency()
        self.build_dir_name = "target/classes"
        self.build_dir = self.process_single_repo()

        self.COMPILE_ERROR = 0
        self.TEST_RUN_ERROR = 0

    def start_single_test(self):
        """
        Run a single method test case with a thread.
        tests directory path, e.g.:
        /data/share/TestGPT_ASE/result/scope_test%20230414210243%d3_1/1460%lang_1_f%ToStringBuilder%append%d3/5
        """
        temp_dir = os.path.join(self.test_path, "temp")
        compiled_test_dir = os.path.join(self.test_path, "runtemp")
        os.makedirs(compiled_test_dir, exist_ok=True)
        try:
            self.instrument(compiled_test_dir, compiled_test_dir)
            test_file = os.path.abspath(glob.glob(temp_dir + '/*.java')[0])
            compiler_output = os.path.join(temp_dir, 'compile_error')
            test_output = os.path.join(temp_dir, 'runtime_error')
            if not self.run_single_test(test_file, compiled_test_dir, compiler_output, test_output):
                return False
            else:
                self.report(compiled_test_dir, temp_dir)
        except Exception as e:
            print(e)
            return False
        return True

    def start_all_test(self):
        """
        Initialize configurations and run all tests
        """
        date = datetime.now().strftime("%Y%m%d%H%M%S")

        # Directories for the test cases, outputs, and reports
        tests_dir = os.path.join(self.target_path, f"tests%{date}")
        compiler_output_dir = os.path.join(tests_dir, "compiler_output")
        test_output_dir = os.path.join(tests_dir, "test_output")
        report_dir = os.path.join(tests_dir, "report")

        compiler_output = os.path.join(compiler_output_dir, "CompilerOutput")
        test_output = os.path.join(test_output_dir, "TestOutput")
        compiled_test_dir = os.path.join(tests_dir, "tests_ChatGPT")

        self.copy_tests(tests_dir)
        return self.run_all_tests(tests_dir, compiled_test_dir, compiler_output, test_output, report_dir)

    def run_all_tests(self, tests_dir, compiled_test_dir, compiler_output, test_output, report_dir):
        """
        Run all test cases in a project.
        """
        tests = os.path.join(tests_dir, "test_cases")
        self.instrument(compiled_test_dir, compiled_test_dir)
        total_compile = 0
        total_test_run = 0
        for t in range(1, 1 + test_number):
            print("Processing attempt: ", str(t))
            for test_case_file in os.listdir(tests):
                if str(t) != test_case_file.split('_')[-1].replace('Test.java', ''):
                    continue
                total_compile += 1
                try:
                    test_file = os.path.join(tests, test_case_file)
                    self.run_single_test(test_file, compiled_test_dir, compiler_output, test_output)
                except Exception as e:
                    print(e)
            self.report(compiled_test_dir, os.path.join(report_dir, str(t)))
            total_test_run = total_compile - self.COMPILE_ERROR
            print("COMPILE TOTAL COUNT:", total_compile)
            print("COMPILE ERROR COUNT:", self.COMPILE_ERROR)
            print("TEST RUN TOTAL COUNT:", total_test_run)
            print("TEST RUN ERROR COUNT:", self.TEST_RUN_ERROR)
            print("\n")
        return total_compile, total_test_run

    def run_single_test(self, test_file, compiled_test_dir, compiler_output, test_output):
        """
        Run a test case.
        :return: Whether it is successful or no.
        """
        if not self.compile(test_file, compiled_test_dir, compiler_output):
            return False
        if os.path.basename(test_output) == 'runtime_error':
            test_output_file = f"{test_output}.txt"
        else:
            test_output_file = f"{test_output}-{os.path.basename(test_file)}.txt"
        cmd = self.java_cmd(compiled_test_dir, test_file)
        try:
            result = subprocess.run(cmd, timeout=TIMEOUT,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                self.TEST_RUN_ERROR += 1
                self.export_runtime_output(result, test_output_file)
                return False
        except subprocess.TimeoutExpired:
            # print(Fore.RED + "TIME OUT!", Style.RESET_ALL)
            return False
        return True

    @staticmethod
    def export_runtime_output(result, test_output_file):
        with open(test_output_file, "w") as f:
            f.write(result.stdout)
            error_msg = result.stderr
            error_msg = re.sub(r'log4j:WARN.*\n?', '', error_msg)
            if error_msg != '':
                f.write(error_msg)

    def compile(self, test_file, compiled_test_dir, compiler_output):
        """
        Compile a test case.
        :param test_file:
        :param compiled_test_dir: the directory to store compiled tests
        :param compiler_output:
        """
        os.makedirs(compiled_test_dir, exist_ok=True)
        cmd = self.javac_cmd(compiled_test_dir, test_file)
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            self.COMPILE_ERROR += 1
            if os.path.basename(compiler_output) == 'compile_error':
                compiler_output_file = f"{compiler_output}.txt"
            else:
                compiler_output_file = f"{compiler_output}-{os.path.basename(test_file)}.txt"
            with open(compiler_output_file, "w") as f:
                f.write(result.stdout)
                f.write(result.stderr)
            return False
        return True

    def process_single_repo(self):
        """
        Return the all build directories of target repository
        """
        if self.has_submodule(self.target_path):
            modules = self.get_submodule(self.target_path)
            postfixed_modules = [f'{self.target_path}/{module}/{self.build_dir_name}' for module in modules]
            build_dir = ':'.join(postfixed_modules)
        else:
            build_dir = os.path.join(self.target_path, self.build_dir_name)
        return build_dir

    @staticmethod
    def get_package(test_file):
        with open(test_file, "r") as f:
            first_line = f.readline()

        package = first_line.strip().replace("package ", "").replace(";", "")
        return package

    @staticmethod
    def is_module(project_path):
        """
        If the path has a pom.xml file and target/classes compiled, a module.
        """
        if not os.path.isdir(project_path):
            return False
        if 'pom.xml' in os.listdir(project_path) and 'target' in os.listdir(project_path):
            return True
        return False

    def get_submodule(self, project_path):
        """
        Get all modules in given project.
        :return: module list
        """
        return [d for d in os.listdir(project_path) if self.is_module(os.path.join(project_path, d))]

    def has_submodule(self, project_path):
        """
        Is a project composed by submodules, e.g., gson
        """
        for dir in os.listdir(project_path):
            if self.is_module(os.path.join(project_path, dir)):
                return True
        return False

    def javac_cmd(self, compiled_test_dir, test_file):
        classpath = f"{JUNIT_JAR}:{MOCKITO_JAR}:{LOG4J_JAR}:{self.dependencies}:{self.build_dir}:."
        classpath_file = os.path.join(compiled_test_dir, 'classpath.txt')
        self.export_classpath(classpath_file, classpath)
        return ["javac", "-d", compiled_test_dir, f"@{classpath_file}", test_file]

    def java_cmd(self, compiled_test_dir, test_file):
        full_test_name = self.get_full_name(test_file)
        classpath = f"{COBERTURA_DIR}/cobertura-2.1.1.jar:{compiled_test_dir}/instrumented:{compiled_test_dir}:" \
                    f"{JUNIT_JAR}:{MOCKITO_JAR}:{LOG4J_JAR}:{self.dependencies}:{self.build_dir}:."
        classpath_file = os.path.join(compiled_test_dir, 'classpath.txt')
        self.export_classpath(classpath_file, classpath)
        if self.coverage_tool == "cobertura":
            return ["java", f"@{classpath_file}",
                    f"-Dnet.sourceforge.cobertura.datafile={compiled_test_dir}/cobertura.ser",
                    "org.junit.platform.console.ConsoleLauncher", "--disable-banner", "--disable-ansi-colors",
                    "--fail-if-no-tests", "--details=none", "--select-class", full_test_name]
        else:  # self.coverage_tool == "jacoco"
            return ["java", f"-javaagent:{JACOCO_AGENT}=destfile={compiled_test_dir}/jacoco.exec",
                    f"@{classpath_file}",
                    "org.junit.platform.console.ConsoleLauncher", "--disable-banner", "--disable-ansi-colors",
                    "--fail-if-no-tests", "--details=none", "--select-class", full_test_name]

    @staticmethod
    def export_classpath(classpath_file, classpath):
        with open(classpath_file, 'w') as f:
            classpath = "-cp " + classpath
            f.write(classpath)
        return

    def get_full_name(self, test_file):
        package = self.get_package(test_file)
        test_case = os.path.splitext(os.path.basename(test_file))[0]
        if package != '':
            return f"{package}.{test_case}"
        else:
            return test_case

    def instrument(self, instrument_dir, datafile_dir):
        """
        Use cobertura scripts to instrument compiled class.
        Generate 'instrumented' directory.
        """
        if self.coverage_tool == "jacoco":
            return
        os.makedirs(instrument_dir, exist_ok=True)
        os.makedirs(datafile_dir, exist_ok=True)
        if 'instrumented' in os.listdir(instrument_dir):
            return
        if self.has_submodule(self.target_path):
            target_classes = os.path.join(self.target_path, '**/target/classes')
        else:
            target_classes = os.path.join(self.target_path, 'target/classes')
        result = subprocess.run(["bash", os.path.join(COBERTURA_DIR, "cobertura-instrument.sh"),
                                 "--basedir", self.target_path,
                                 "--destination", f"{instrument_dir}/instrumented",
                                 "--datafile", f"{datafile_dir}/cobertura.ser",
                                 target_classes], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def report(self, datafile_dir, report_dir):
        """
        Generate coverage report by given coverage tool.
        """
        os.makedirs(report_dir, exist_ok=True)
        if self.coverage_tool == "cobertura":
            result = subprocess.run(["bash", os.path.join(COBERTURA_DIR, "cobertura-report.sh"),
                                     "--format", REPORT_FORMAT, "--datafile", f"{datafile_dir}/cobertura.ser",
                                     "--destination",
                                     report_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            build_list = self.build_dir.split(":")
            classfiles = ""
            for build in build_list:
                classfiles += " --classfiles " + build
            result = subprocess.run(
                ["java", "-jar", JACOCO_CLI, "report", f"{datafile_dir}/jacoco.exec", classfiles,
                 "--csv", os.path.join(report_dir, "coverage.csv")], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

    def make_dependency(self):
        """
        Generate runtime dependencies of a given project
        """
        mvn_dependency_dir = 'target/dependency'
        deps = []
        if not self.has_made():
            # Run mvn command to generate dependencies
            # print("Making dependency for project", self.target_path)
            subprocess.run(
                f"mvn dependency:copy-dependencies -DoutputDirectory={mvn_dependency_dir} -f {self.target_path}/pom.xml",
                shell=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(f"mvn install -DskipTests -f {self.target_path}/pom.xml", shell=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        dep_jars = glob.glob(self.target_path + "/**/*.jar", recursive=True)
        deps.extend(dep_jars)
        deps = list(set(deps))
        return ':'.join(deps)

    def has_made(self):
        """
        If the project has made before
        """
        for dirpath, dirnames, filenames in os.walk(self.target_path):
            if 'pom.xml' in filenames and 'target' in dirnames:
                target = os.path.join(dirpath, 'target')
                if 'dependency' in os.listdir(target):
                    return True
        return False

    def copy_tests(self, target_dir):
        """
        Copy test cases of given project to target path for running.
        :param target_dir: path to target directory used to store test cases
        """
        tests = glob.glob(self.test_path + "/**/*Test.java", recursive=True)
        target_project = os.path.basename(self.target_path.rstrip('/'))
        _ = [os.makedirs(os.path.join(target_dir, dir_name), exist_ok=True) for dir_name in
             ("test_cases", "compiler_output", "test_output", "report")]
        print("Copying tests to ", target_project, '...')
        for tc in tests:
            # tc should be 'pathto/project/testcase'.
            tc_project = tc.split('/')[-4].split('%')[1]
            if tc_project != target_project or \
                    not os.path.exists(self.target_path):
                continue
            os.system(f"cp {tc} {os.path.join(target_dir, 'test_cases')}")
