import copy
import json
import os.path
import datetime
import re
import shutil
import time

import openai
from config import *
from tools import *
import random
import concurrent.futures
import javalang
import jinja2
from colorama import Fore, Style, init
from run_tests import start_test, run_with_d4j
from parse_response import export_method_test_case, change_class_name, repair_package, repair_imports

init()

# Create a jinja2 environment
env = jinja2.Environment(loader=jinja2.FileSystemLoader('../prompt'))

# TODO: new projects
template_names = {
    "no_deps": "d1_4.jinja2",
    "with_deps": "d3_4.jinja2",
    "error": "error_3.jinja2",
}
# TODO: d4j projects, checkout java version to 11
# template_names = {
#     "no_deps": "d1_6.jinja2",
#     "with_deps": "d3_6.jinja2",
#     "error": "error_4.jinja2",
#     "process_error": "process_error.jinja2",
# }


def get_current_time():
    """
    Get current time
    :return:
    """
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%H:%M:%S")
    return formatted_time


def ask_chatgpt_thread(idx, messages, save_path):
    """
    Threaded version of ask_chatgpt
    :return: [{"role":"user","content":"..."}]
    """
    # print(get_current_time(), idx, "Started...")
    # Send a request to OpenAI
    if get_messages_tokens(messages) > MAX_PROMPT_TOKENS:  # no need to send request
        return False
    openai.api_key = random.choice(api_keys)
    max_try = 5
    while max_try:
        try:
            completion = openai.ChatCompletion.create(messages=messages,
                                                      model=model,
                                                      temperature=temperature,
                                                      top_p=top_p,
                                                      frequency_penalty=frequency_penalty,
                                                      presence_penalty=presence_penalty)
            with open(save_path, "w") as f:
                json.dump(completion, f)
            # print(get_current_time(), idx, "Finished!")
            return True
        except Exception as e:
            print(Fore.RED, e, Style.RESET_ALL)
            if "This model's maximum context length is 4097 tokens." in str(e):
                break
            time.sleep(10)
            if "Rate limit reached" in str(e):
                sleep_time = random.randint(60, 120)
                time.sleep(sleep_time)
        max_try -= 1
    return False


def ask_chatgpt(messages):
    """
    Single thread ask chatgpt.
    :param messages: [{"role":"user","content":"..."}]
    :return:
    """
    openai.api_key = random.choice(api_keys)
    completion = openai.ChatCompletion.create(messages=messages,
                                              model=model,
                                              temperature=temperature,
                                              top_p=top_p,
                                              frequency_penalty=frequency_penalty,
                                              presence_penalty=presence_penalty)
    return completion


def generate_prompt(template_name, context: dict):
    """
    Generate prompt via jinja2 engine
    :param template_name:
    :param context:
    :return:
    """
    # Load template
    template = env.get_template(template_name)
    prompt = template.render(context)

    return prompt


def generate_messages(template_name, context_file: (str, dict)):
    """
    You can modify this function or create new function to add more information
    :param template_name:
    :param context_file:
    :return:
    """
    if isinstance(context_file, str):
        with open(context_file, "r") as f:
            context = json.load(f)
    else:
        context = context_file
    messages = []
    system_name = template_name.split(".")[0] + "_system" + ".jinja2"
    if os.path.exists(os.path.join("../prompt", system_name)):
        system_message = generate_prompt(system_name, {})
        messages.append({"role": "system", "content": system_message})
    content = generate_prompt(template_name, context)
    messages.append({"role": "user", "content": content})

    return messages


def start_generation(dataset_dir, template_name, result_dir):  # For scope test only
    if not os.path.exists(dataset_dir):
        raise RuntimeError("Dataset path not found!")
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    # Get a list of all file paths
    file_paths = []
    for root, dirs, files in os.walk(dataset_dir):
        for file in files:
            if file.endswith(".json"):
                file_paths.append(os.path.join(root, file))

    # Create a thread pool with maximum of thread_number
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_number) as executor:
        for idx, file_path in enumerate(file_paths):
            messages = generate_messages(template_name, file_path)
            # print(messages)
            base_dir, base_name = os.path.split(file_path.replace("/dataset/", "/result/"))
            for test_n in range(1, test_number + 1):
                # Create subdirectories for each test
                current_dir = os.path.join(base_dir, str(test_n))
                if not os.path.exists(current_dir):
                    os.makedirs(current_dir)
                save_path = os.path.join(current_dir, base_name[:-5] + "_" + str(test_n) + ".json")
                if os.path.exists(save_path):
                    print(file_path, "Already exist. Skipped!")
                    continue
                executor.submit(ask_chatgpt_thread, str(idx) + "_test_" + str(test_n), messages, save_path)
    print("Main thread executing!")


def complete_code(code):
    """
    To complete the code
    :param code:
    :return:
    """

    # We delete the last incomplete test.
    code = code.split("@Test\n")
    code = "@Test\n".join(code[:-1]) + '}'
    return code


def process_error_message(error_message, allowed_tokens):
    """
    Process the error message
    :param error_message:
    :param allowed_tokens:
    :return:
    """
    if allowed_tokens <= 0:
        return ""
    while count_tokens(error_message) > allowed_tokens:
        if len(error_message) > 50:
            error_message = error_message[:-50]
        else:
            break
    return error_message


def if_code_is_valid(code) -> bool:
    """
    Check if the code is valid
    :param code:
    :return: True or False
    """
    if "{" not in code or "}" not in code:
        return False
    try:
        javalang.parse.parse(code)
        return True
    except Exception:
        return False


def syntactic_check(code):
    """
    Syntactic repair
    :param code:
    :return: has_syntactic_error, code
    """
    if is_syntactic_correct(code):
        return False, code
    else:
        stop_point = [";", "}", "{", " "]  # Stop point
        for idx in range(len(code) - 1, -1, -1):
            if code[idx] in stop_point:
                code = code[:idx + 1]
                break
        left_bracket = code.count("{")
        right_bracket = code.count("}")
        for idx in range(left_bracket - right_bracket):
            code += "}\n"

        if is_syntactic_correct(code):
            return True, code

        matches = list(re.finditer(r"(?<=\})[^\}]+(?=@)", code))
        if matches:
            code = code[:matches[-1].start() + 1]
            left_count = code.count("{")
            right_count = code.count("}")
            for _ in range(left_count - right_count):
                code += "\n}"
        if is_syntactic_correct(code):
            return True, code
        else:
            return True, ""


def is_syntactic_correct(code):
    """
    Check if the code is syntactically correct
    :param code:
    :return:
    """
    try:
        javalang.parse.parse(code)
        return True
    except Exception as e:
        # print(e)
        return False


def extract_code(string):
    """
    Check if the string is valid code
    :param string:
    :return: has_code, extracted_code, has_syntactic_error
    """
    # if the string is valid code, return True
    try:
        javalang.parse.parse(string)
        return True, string, False
    except Exception as E:
        pass

    has_code = False
    extracted_code = ""
    has_syntactic_error = False

    # Define regex pattern to match the code blocks
    pattern = r"```[java]*([\s\S]*?)```"

    # Find all matches in the text
    matches = re.findall(pattern, string)
    if matches:
        # Filter matches to only include ones that contain "@Test"
        filtered_matches = [match.strip() for match in matches if
                            "@Test" in match and "class" in match and "import" in match]
        if filtered_matches:
            for match in filtered_matches:
                has_syntactic_error, extracted_code = syntactic_check(match)
                if extracted_code != "":
                    has_code = True
                    break

    if not has_code:
        if "```java" in string:
            separate_string = string.split("```java")[1]
            if "@Test" in separate_string:
                has_syntactic_error, temp_code = syntactic_check(separate_string)
                if temp_code != "":
                    extracted_code = temp_code
                    has_code = True
        elif "```" in string:
            separate_strings = string.split("```")
            for separate_string in separate_strings:
                if "@Test" in separate_string:
                    has_syntactic_error, temp_code = syntactic_check(separate_string)
                    if temp_code != "":
                        extracted_code = temp_code
                        has_code = True
                        break
        else:  # Define boundary
            allowed = ["import", "packages", "", "@"]
            code_lines = string.split("\n")
            start, anchor, end = -1, -1, -1
            allowed_lines = [False for _ in range(len(code_lines))]
            left_brace = {x: 0 for x in range(len(code_lines))}
            right_brace = {x: 0 for x in range(len(code_lines))}
            for i, line in enumerate(code_lines):
                left_brace[i] += line.count("{")
                right_brace[i] += line.count("}")
                striped_line = line.strip()

                for allow_start in allowed:
                    if striped_line.startswith(allow_start):
                        allowed_lines[i] = True
                        break

                if re.search(r'public class .*Test', line) and anchor == -1:
                    anchor = i

            if anchor != -1:
                start = anchor
                while start:
                    if allowed_lines[start]:
                        start -= 1

                end = anchor
                left_sum, right_sum = 0, 0
                while end < len(code_lines):
                    left_sum += left_brace[end]
                    right_sum += right_brace[end]
                    if left_sum == right_sum and left_sum >= 1 and right_sum >= 1:
                        break
                    end += 1

                temp_code = "\n".join(code_lines[start:end + 1])
                has_syntactic_error, temp_code = syntactic_check(temp_code)
                if temp_code != "":
                    extracted_code = temp_code
                    has_code = True

    extracted_code = extracted_code.strip()
    return has_code, extracted_code, has_syntactic_error


def extract_and_run(input_string, output_path, class_name, method_id, test_num, project_name, package):
    """
    Extract the code and run it
    :param project_name:
    :param test_num:
    :param method_id:
    :param class_name:
    :param input_string:
    :param output_path:
    :return:
    """
    result = {}
    # 1. Extract the code
    has_code, extracted_code, has_syntactic_error = extract_code(input_string)
    if not has_code:
        return False, True
    result["has_code"] = has_code
    result["source_code"] = extracted_code
    if package:
        result["source_code"] = repair_package(extracted_code, package)
    result["has_syntactic_error"] = has_syntactic_error
    # 2. Run the code
    temp_dir = os.path.join(os.path.dirname(output_path), "temp")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    export_method_test_case(os.path.abspath(temp_dir), class_name, method_id, test_num,
                            change_class_name(result["source_code"], class_name, method_id, test_num))

    # run test
    response_dir = os.path.abspath(os.path.dirname(output_path))
    target_dir = os.path.abspath(os.path.join(projects_dir, project_name))
    start_test(response_dir, target_dir)

    # 3. Read the result
    if "compile_error.txt" in os.listdir(temp_dir):
        with open(os.path.join(temp_dir, "compile_error.txt"), "r") as f:
            result["compile_error"] = f.read()

    if "runtime_error.txt" in os.listdir(temp_dir):
        with open(os.path.join(temp_dir, "runtime_error.txt"), "r") as f:
            result["runtime_error"] = f.read()
    if "coverage.html" in os.listdir(temp_dir):
        result["coverage_html"] = True
    if "coverage.xml" in os.listdir(temp_dir):
        result["coverage_xml"] = True

    test_passed = False
    if "coverage_xml" in result or "coverage_html" in result:
        test_passed = True

    # 4. Save the result
    with open(output_path, "w") as f:
        json.dump(result, f)

    return test_passed, False


def remain_prompt_tokens(messages):
    return MAX_PROMPT_TOKENS - get_messages_tokens(messages)


def whole_process_thread(thread_id, test_num, base_dir, repair, submits, total):
    """
    Threaded version of start_generation
    :param save_dir:
    :param repair:
    :param thread_id:
    :return:
    """
    progress = '[' + str(submits) + ' / ' + str(total) + ']'
    # Create subdirectories for each test
    save_dir = os.path.join(base_dir, str(test_num))
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    run_temp_dir = os.path.join(save_dir, "runtemp")

    steps, rounds = 0, 0
    method_id, project_name, class_name, method_name = parse_directory_name(base_dir)

    # 1. Get method data
    with open(get_dataset_path(method_id, project_name, class_name, method_name, "raw"), "r") as f:
        raw_data = json.load(f)

    package = raw_data["package"]
    imports = raw_data["imports"]

    # 2. Get data from direction_1 as well as direction_3
    with open(get_dataset_path(method_id, project_name, class_name, method_name, 1), "r") as f:
        context_d_1 = json.load(f)
    with open(get_dataset_path(method_id, project_name, class_name, method_name, 3), "r") as f:
        context_d_3 = json.load(f)

    def _remove_imports_context(strings):
        if imports:
            strings = strings.replace(imports, "")
        if package:
            strings = strings.replace(package, "")
        strings = strings.strip()
        return strings

    try:
        while rounds < max_rounds:
            # 1. Ask GPT
            steps += 1
            rounds += 1
            print(progress, method_id, "test_" + str(test_num), "Asking ChatGPT...", "rounds", rounds)
            gpt_file_name = os.path.join(save_dir, str(steps) + "_GPT_" + str(rounds) + ".json")
            # Need to generate new messages
            if rounds != 1:
                last_round_result = get_latest_file(save_dir)
                with open(last_round_result, "r") as f:
                    last_round_result = json.load(f)
                last_raw = get_latest_file(save_dir, suffix="raw")
                with open(last_raw, "r") as f:
                    last_raw = json.load(f)

                # Prepare the error message
                context = {"class_name": context_d_1["class_name"], "method_name": context_d_1["focal_method"],
                           "unit_test": last_raw["source_code"], "method_code": context_d_1["information"]}
                # Required, cannot truncate

                # Adaptive generate error message
                messages = generate_messages(template_names["error"], context)
                allow_tokens = remain_prompt_tokens(messages)
                if allow_tokens < MIN_ERROR_TOKENS:
                    context["method_code"] = _remove_imports_context(context["method_code"])
                    messages = generate_messages(template_names["error"], context)
                    allow_tokens = remain_prompt_tokens(messages)
                if allow_tokens < MIN_ERROR_TOKENS:
                    context["method_code"] = context_d_3["full_fm"]
                    messages = generate_messages(template_names["error"], context)
                    allow_tokens = remain_prompt_tokens(messages)
                if allow_tokens < MIN_ERROR_TOKENS:
                    context["method_code"] = _remove_imports_context(context_d_3["full_fm"])
                    messages = generate_messages(template_names["error"], context)
                    allow_tokens = remain_prompt_tokens(messages)
                if allow_tokens >= MIN_ERROR_TOKENS:
                    if "compile_error" in last_round_result:
                        context["error_type"] = "compiling"
                        error_mes = process_error_message(last_round_result["compile_error"], allow_tokens)
                        context["error_message"] = error_mes
                    if "runtime_error" in last_round_result:
                        context["error_type"] = "running"
                        error_mes = process_error_message(last_round_result["runtime_error"], allow_tokens)
                        context["error_message"] = error_mes
                else:
                    print(progress, Fore.RED, method_id, "Tokens not enough, test fatal error...", Style.RESET_ALL)  # Fatal error
                    break
                if "compile_error" not in last_round_result and "runtime_error" not in last_round_result:
                    print(progress, Fprogress, ore.RED, method_id, "Timeout error, test fatal error...", Style.RESET_ALL)
                    break
                messages = generate_messages(template_names["error"], context)
                # print('-------------------')
                # print(context["error_message"])
            else:  # Direction_1 or Direction_3
                if not context_d_3["c_deps"] and not context_d_3["m_deps"]:  # No dependencies d_1
                    context = copy.deepcopy(context_d_1)
                    messages = generate_messages(template_names["no_deps"], context)
                    if remain_prompt_tokens(messages) < 0:  # Truncate information
                        context["information"] = _remove_imports_context(context["information"])
                        messages = generate_messages(template_names["no_deps"], context)
                        if remain_prompt_tokens(messages) < 0:  # Failed generating messages
                            messages = []
                else:  # Has dependencies d_3
                    context = copy.deepcopy(context_d_3)
                    messages = generate_messages(template_names["with_deps"], context)
                    if remain_prompt_tokens(messages) < 0:  # Need Truncate information
                        context["full_fm"] = _remove_imports_context(context["full_fm"])
                        messages = generate_messages(template_names["with_deps"], context)
                        if remain_prompt_tokens(messages) < 0:  # Failed generating messages
                            messages = []

                if not messages:  # Turn to minimum messages
                    context = copy.deepcopy(context_d_1)  # use direction 1 as template
                    context["information"] = context_d_3["full_fm"]  # use full_fm d_3 as context
                    messages = generate_messages(template_names["no_deps"], context)
                    if remain_prompt_tokens(messages) < 0:
                        context["information"] = _remove_imports_context(context["information"])
                        messages = generate_messages(template_names["no_deps"], context)  # !! MINIMUM MESSAGES!!
                        if remain_prompt_tokens(messages) < 0:  # Failed generating messages
                            print(progress, Fore.RED, "Tokens not enough, test fatal error...", Style.RESET_ALL)
                            break
                # print(Fore.BLUE, messages[1]['content'], Style.RESET_ALL)

            status = ask_chatgpt_thread(thread_id, messages, gpt_file_name)
            if not status:
                print(progress, Fore.RED, 'OpenAI Fail processing messages', Style.RESET_ALL)
                break

            with open(gpt_file_name, "r") as f:
                gpt_result = json.load(f)

            # 2. Extract information from GPT, and RUN save the result
            steps += 1
            print(progress, method_id, "test_" + str(test_num), "Extracting information", "rounds", rounds)
            raw_file_name = os.path.join(save_dir, str(steps) + "_raw_" + str(rounds) + ".json")

            # run test. save the result in raw_file_name
            input_string = gpt_result["choices"][0]['message']["content"]
            test_passed, fatal_error = extract_and_run(input_string, raw_file_name, class_name, method_id, test_num,
                                                       project_name,
                                                       package)

            if test_passed:
                print(progress, Fore.GREEN, method_id, "test_" + str(test_num), "steps", steps, "rounds", rounds, "test passed",
                      Style.RESET_ALL)
                break

            if not os.path.exists(raw_file_name):
                print(progress, Fore.RED, method_id, "test_" + str(test_num), "steps", steps, "rounds", rounds,
                      "no code in raw result", Style.RESET_ALL)
                break

            # Open up the raw result
            with open(get_latest_file(save_dir), "r") as f:
                raw_result = json.load(f)

            # 4. Start imports Repair
            steps += 1
            print(progress, method_id, "test_" + str(test_num), "Fixing imports", "rounds", rounds)
            imports_file_name = os.path.join(save_dir, str(steps) + "_imports_" + str(rounds) + ".json")
            # run imports repair
            source_code = raw_result["source_code"]
            source_code = repair_imports(source_code, imports)
            test_passed, fatal_error = extract_and_run(source_code, imports_file_name, class_name, method_id, test_num,
                                                       project_name,
                                                       package)
            if test_passed:
                print(progress, Fore.GREEN, method_id, "test_" + str(test_num), "steps", steps, "rounds", rounds, "test passed",
                      Style.RESET_ALL)
                break
            if fatal_error:
                print(progress, Fore.RED, method_id, "test_" + str(test_num), "steps", steps, "rounds", rounds, "fatal error",
                      Style.RESET_ALL)
                break

            print(progress, Fore.YELLOW, method_id, "test_" + str(test_num), "Test failed, fixing...", "rounds", rounds,
                  Style.RESET_ALL)
            if not repair:  # If we do not want to repair the code, we don't need to second round
                break
    except Exception as e:
        print(progress, Fore.RED, e, Style.RESET_ALL)
    if os.path.exists(run_temp_dir):
        run_temp_dir = os.path.abspath(run_temp_dir)
        shutil.rmtree(run_temp_dir)


def start_whole_process(source_dir, threaded=False, repair=True):
    """
    Start repair process
    :param repair:  Whether to repair the code
    :param threaded: Whether to use multi-threading
    :param source_dir: The directory of the dataset or scoped dataset.
    :return:
    """
    # Get a list of all file paths
    file_paths = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".json"):
                file_paths.append(os.path.join(root, file))

    if threaded:
        print("Multi threads executing!")
        # Create a thread pool with maximum of thread_number
        with concurrent.futures.ProcessPoolExecutor(max_workers=thread_number) as executor:
            submits = 0
            total = len(file_paths) * test_number
            for idx, file_path in enumerate(file_paths):
                base_dir, base_name = os.path.split(file_path.replace("/dataset/", "/result/"))
                for test_num in range(1, test_number + 1):
                    submits += 1
                    executor.submit(whole_process_thread, str(idx) + "_test", test_num, base_dir, repair, submits, total)
        print("Main thread executing!")
    else:
        print("Single thread executing!")
        for idx, file_path in enumerate(file_paths):
            base_dir, base_name = os.path.split(file_path.replace("/dataset/", "/result/"))
            for test_num in range(1, test_number + 1):
                whole_process_thread(str(idx) + "_test_", test_num, base_dir, repair=repair)


if __name__ == '__main__':
    dataset_directory = '../dataset/test_04091730_d1'
    result_directory = '../result/test_04091730_d1'
    template_file = 'd1_1.jinja2'
    print("Dataset directory:", dataset_directory)
    print("Result directory:", result_directory)
    confirm = input("Are you sure to continue? (y/n) ")
    if confirm == "y":
        start_generation(dataset_directory, template_file, result_directory)
        print("Finished!")
    else:
        print("Canceled!")
