import copy
import datetime
from askGPT import extract_code
from tools import *

count_template = {"correct": 0, "failed": 0, "passed": 0, "syntax_error": 0, "compile_error": 0, "total": 0,
                  "methods": {}}

no_temp_dir = []


class Summary(object):
    def __init__(self, root_dir):
        self.root_dir = root_dir
        # all -- info --
        self.repair_round_count = {str(x): 0 for x in range(1, 7)}  # repair round count
        self.raw_count = {"correct": 0, "passed": 0, "runtime_error": 0, "compile_error": 0, "syntax_error": 0}
        self.raw_rule_count = {"correct": 0, "passed": 0, "runtime_error": 0, "compile_error": 0, "syntax_error": 0}
        self.raw_rule_repair_count = {"correct": 0, "passed": 0, "runtime_error": 0, "compile_error": 0,
                                      "syntax_error": 0}
        self.total_count = {"total_tests": 0, "total_java_files": 0, "total_methods": 0}
        self.project_count = {}
        self.token_count = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "all_files": 0}
        # single test -- info --
        self.method_dir = None
        self.current_dir = None
        self.round_number: (None, str) = None
        self.file_java = None
        self.file_json = None
        self.file_gpt_1 = None
        self.file_raw_1 = None
        self.file_imports_1 = None
        self.file_last = None
        self.has_runtime_error = False
        self.has_compile_error = False

        # Basic info ---
        self.project_name = None
        self.class_name = None
        self.method_name = None
        self.test_number = None
        self.method_id = None

    def reset_test(self):
        """
        pass
        :return:
        """
        self.method_dir = None
        self.round_number = "0"
        self.current_dir = None
        self.file_java = None
        self.file_json = None
        self.file_gpt_1 = None
        self.file_raw_1 = None
        self.file_imports_1 = None
        self.file_last = None
        self.has_runtime_error = False
        self.has_compile_error = False

        self.project_name = None
        self.class_name = None
        self.method_name = None
        self.test_number = None
        self.method_id = None

    def init_test(self, directory_path):
        self.current_dir = directory_path
        self.test_number = os.path.basename(self.current_dir)
        test_base_dir = os.path.dirname(directory_path)
        self.method_dir = os.path.basename(test_base_dir)
        self.parse_name()
        self.open_test()
        if self.project_name not in self.project_count:
            self.project_count[self.project_name] = copy.deepcopy(count_template)

    def parse_name(self):
        self.method_id, self.project_name, self.class_name, self.method_name = parse_directory_name(self.method_dir)
        if self.project_name.startswith("Chart_"):
            self.project_name = "Chart"
        elif self.project_name.startswith("Lang_"):
            self.project_name = "Lang"
        elif self.project_name.startswith("Cli_"):
            self.project_name = "Cli"
        elif self.project_name.startswith("Csv_"):
            self.project_name = "Csv"
        elif self.project_name.startswith("Gson_"):
            self.project_name = "Gson"

    def save(self):
        """
        Result save
        """
        now = datetime.datetime.now()
        formatted_time = now.strftime("%m-%d_%H-%M-%S")
        result = {"repair_round_count": self.repair_round_count, "raw_count": self.raw_count,
                  "raw_rule_count": self.raw_rule_count, "raw_rule_repair_count": self.raw_rule_repair_count,
                  "total_count": self.total_count, "project_count": self.project_count, "token_count": self.token_count}

        with open(os.path.join(self.root_dir, "summary" + formatted_time + ".json"), "w") as f:
            json.dump(result, f, indent=4)

        print("Repair round count: {}".format(self.repair_round_count))
        print("Raw count: {}".format(self.raw_count))
        print("Raw rule count: {}".format(self.raw_rule_count))
        print("Raw rule repair count: {}".format(self.raw_rule_repair_count))
        print("Project count: {}".format(self.project_count))
        print("Token count: {}".format(self.token_count))

    def open_test(self):
        """
        :return:
        """
        global no_temp_dir
        temp_dir = os.path.join(self.current_dir, "temp")
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                if filename.endswith(".java"):
                    with open(os.path.join(temp_dir, filename), "r") as f:
                        self.file_java = f.read()
                        break
        else:
            no_temp_dir.append(self.current_dir)

        json_path = os.path.join(self.current_dir, "temp", "coverage.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                self.file_json = json.load(f)

        runtime_path = os.path.join(self.current_dir, "temp", "runtime_error.txt")
        if os.path.exists(runtime_path):
            self.has_runtime_error = True

        compile_path = os.path.join(self.current_dir, "temp", "compile_error.txt")
        if os.path.exists(compile_path):
            self.has_compile_error = True

        self.round_number = "0"
        for filename in os.listdir(self.current_dir):
            if os.path.isfile(os.path.join(self.current_dir, filename)):
                rounds = filename.split("_")[-1].split(".")[0]
                if rounds > self.round_number:
                    self.round_number = rounds

        path_gpt_1 = os.path.join(self.current_dir, "1_gpt_1.json")
        if os.path.exists(path_gpt_1):
            with open(path_gpt_1, "r") as f:
                self.file_gpt_1 = json.load(f)

        path_file_raw_1 = os.path.join(self.current_dir, "2_raw_1.json")
        if os.path.exists(path_file_raw_1):
            with open(path_file_raw_1, "r") as f:
                self.file_raw_1 = json.load(f)

        path_file_imports_1 = os.path.join(self.current_dir, "3_imports_1.json")
        if os.path.exists(path_file_imports_1):
            with open(path_file_imports_1, "r") as f:
                self.file_imports_1 = json.load(f)

        path_file_last = get_latest_file(self.current_dir)
        if path_file_last != "":
            with open(path_file_last, "r") as f:
                self.file_last = json.load(f)

    def summarize_test(self):
        """
        Summarize the test
        :return: 
        """
        self.project_count[self.project_name]["total"] += 1
        if self.method_id not in self.project_count[self.project_name]["methods"]:
            self.project_count[self.project_name]["methods"][self.method_id] = False

        if "_GPT_" not in get_latest_file(self.current_dir):
            print(self.current_dir)
            if self.file_last["has_syntactic_error"]:
                self.project_count[self.project_name]["syntax_error"] += 1

        else:  # GPT run_extract again
            content = get_openai_content(self.file_last)
            has_code, extracted_code, has_syntactic_error = extract_code(content)
            if has_syntactic_error:
                self.project_count[self.project_name]["syntax_error"] += 1

        if self.has_runtime_error:
            self.project_count[self.project_name]["failed"] += 1

        if self.has_compile_error:
            self.project_count[self.project_name]["compile_error"] += 1

        if self.file_json:
            self.project_count[self.project_name]["passed"] += 1

            if self.file_java and self.is_correct(self.file_java, self.method_name):
                self.project_count[self.project_name]["correct"] += 1
                self.project_count[self.project_name]["methods"][self.method_id] = True

    @staticmethod
    def is_correct(code, method_name):
        if code.count("assert") >= 1 and code.count(method_name) >= 1 and code.count("@Test") >= 1:
            return True
        return False

    def summarize_components(self):
        """ 
        Summarize the rounds information
        :return:
        """  # {"correct": 0, "passed": 0, "runtime_error": 0, "compile_error": 0, "syntax_error": 0}
        if self.file_json:
            self.repair_round_count[self.round_number] += 1

        if self.file_raw_1:
            if self.file_raw_1["has_syntactic_error"]:
                self.raw_count["syntax_error"] += 1
            if "compile_error" in self.file_raw_1 and self.file_raw_1["compile_error"]:
                self.raw_count["compile_error"] += 1
            if "runtime_error" in self.file_raw_1 and self.file_raw_1["runtime_error"]:
                self.raw_count["runtime_error"] += 1
            if "coverage_xml" in self.file_raw_1 and self.file_raw_1["coverage_xml"]:
                self.raw_count["passed"] += 1
                if self.is_correct(self.file_raw_1["source_code"], self.method_name):
                    self.raw_count["correct"] += 1

        if self.file_imports_1:
            if self.file_imports_1["has_syntactic_error"]:
                self.raw_rule_count["syntax_error"] += 1
            if "compile_error" in self.file_imports_1 and self.file_imports_1["compile_error"]:
                self.raw_rule_count["compile_error"] += 1
            if "runtime_error" in self.file_imports_1 and self.file_imports_1["runtime_error"]:
                self.raw_rule_count["runtime_error"] += 1
            if "coverage_xml" in self.file_imports_1 and self.file_imports_1["coverage_xml"]:
                self.raw_rule_count["passed"] += 1
                if self.is_correct(self.file_imports_1["source_code"], self.method_name):
                    self.raw_rule_count["correct"] += 1

        if "_GPT_" not in get_latest_file(self.current_dir):
            if self.file_last["has_syntactic_error"]:
                self.raw_rule_repair_count["syntax_error"] += 1
            if "compile_error" in self.file_last and self.file_last["compile_error"]:
                self.raw_rule_repair_count["compile_error"] += 1
            if "runtime_error" in self.file_last and self.file_last["runtime_error"]:
                self.raw_rule_repair_count["runtime_error"] += 1
            if "coverage_xml" in self.file_last and self.file_last["coverage_xml"]:
                self.raw_rule_repair_count["passed"] += 1
                if self.is_correct(self.file_last["source_code"], self.method_name):
                    self.raw_rule_repair_count["correct"] += 1

    def summarize_token(self):
        """
        Count the token
        :param code:
        :return:
        """
        self.token_count["prompt_tokens"] += self.file_gpt_1["usage"]["prompt_tokens"]
        self.token_count["completion_tokens"] += self.file_gpt_1["usage"]["completion_tokens"]
        self.token_count["total_tokens"] += self.file_gpt_1["usage"]["total_tokens"]
        self.token_count["all_files"] += 1

    def run(self):
        """
        Run the summary
        :return:
        """
        # walk over directory
        for directory_path, directory_names, file_names in os.walk(self.root_dir):
            # Find if the file is 1_GPT_1.json
            if os.path.exists(os.path.join(directory_path, "1_GPT_1.json")):
                self.reset_test()
                self.init_test(directory_path)
                self.summarize_test()
                self.summarize_token()
                self.summarize_components()
        self.save()


if __name__ == '__main__':
    root_dir = "~/Desktop/result_428/a_5_result_428"
    summary = Summary(root_dir)
    summary.run()
    print(no_temp_dir)
