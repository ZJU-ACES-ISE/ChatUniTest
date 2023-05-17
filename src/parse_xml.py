from tools import *
from bs4 import BeautifulSoup


def xml_to_json(result_path):
    """

    :param result_path:
    :return:
    """
    output_path = os.path.abspath(result_path[:-4] + ".json")
    if os.path.exists(output_path):  # if the file already exists
        return
    src_path = os.path.abspath(result_path)
    with open(src_path, "r") as f:
        soup = BeautifulSoup(f, "xml")
    result = {"line-rate": soup.find("coverage").attrs["line-rate"],
              "branch-rate": soup.find("coverage").attrs["branch-rate"],
              "lines-covered": soup.find("coverage").attrs["lines-covered"],
              "branches-covered": soup.find("coverage").attrs["branches-covered"],
              "branches-valid": soup.find("coverage").attrs["branches-valid"],
              "complexity": soup.find("coverage").attrs["complexity"]}
    with open(output_path, "w") as f:
        json.dump(result, f)


def get_numberutils_result(result_path=None):
    """

    :param result_path:
    :return:
    """
    if result_path is None:
        result_path = find_newest_result()
    final_result = {}
    for name in os.listdir(result_path):
        file_path = os.path.join(result_path, name)
        if os.path.isdir(file_path):
            m_id, project_name, class_name, method_name = parse_file_name(name)
            raw_data = get_raw_data(m_id, project_name, class_name, method_name)
            parameters = raw_data["parameters"]
            for i in range(1, test_number + 1):
                runtemp_path = os.path.join(file_path, str(i), "runtemp")
                if os.path.exists(runtemp_path):
                    shutil.rmtree(runtemp_path)
                coverage_path = os.path.join(file_path, str(i), "temp", "coverage.json")
                if os.path.exists(coverage_path):
                    with open(coverage_path, "r") as f:
                        coverage = json.load(f)
                    if parameters not in final_result:
                        final_result[parameters] = {"line-covered": 0,
                                                    "coverage_path": ""}
                    covered = eval(coverage["lines-covered"])
                    if covered > final_result[parameters]["line-covered"]:
                        final_result[parameters] = {"line-covered": covered,
                                                    "coverage_path": coverage_path}
    # print(final_result)
    compare_list = ["toInt(String, int)", "toLong(String, long)", "toFloat(String, float)", "toDouble(String, double)",
                    "toByte(String, byte)", "toShort(String, short)", "createFloat(String)", "createDouble(String)",
                    "createInteger(String)", "createLong(String)", "createBigInteger(String)",
                    "createBigDecimal(String)", "min(long[])", "min(int, int, int)", "max(float[])",
                    "max(byte, byte, byte)", "isDigits(String)", "isNumber(String)"]
    for key in compare_list:
        print(key, final_result[key]["line-covered"])
        # print(key, final_result[key]["line-covered"], final_result[key]["coverage_path"])
    with open(os.path.join(result_path, "numberutils_result.json"), "w") as f:
        json.dump(final_result, f)


def result_analysis(result_path=None):
    if not result_path:
        result_path = find_newest_result()
    if not os.path.exists(result_path):
        raise RuntimeError("Result Path not found!")
    print("\n" + result_path)
    # Parse result to json
    for directory_path, directory_names, file_names in os.walk(result_path):
        for file_name in file_names:
            if file_name == 'coverage.xml':  # check if the file name is 'coverage.xml'
                file_path = os.path.join(directory_path, file_name)
                xml_to_json(file_path)

    all_files_cnt = 0
    all_java_files_cnt = 0
    success_cnt = 0
    success_cnt_json = 0
    fail_cnt = 0
    runtemp_cnt = 0
    repair_success_cnt = 0
    repair_failed_cnt = 0
    project_name = ""
    repair_rounds = {i: 0 for i in range(2, max_rounds + 1)}
    for name in os.listdir(result_path):
        directory_name = os.path.join(result_path, name)
        if os.path.isdir(directory_name):
            if not project_name:
                project_name = parse_file_name(directory_name)[1]
            all_files_cnt += len(os.listdir(directory_name))
            for i in range(1, test_number + 1):
                sub_dir = os.path.join(directory_name, str(i))
                if os.path.exists(sub_dir):
                    runtemp_path = os.path.abspath(os.path.join(sub_dir, "runtemp/"))
                    if os.path.exists(runtemp_path):
                        runtemp_cnt += 1
                        shutil.rmtree(runtemp_path)

                    temp_dir = os.path.join(sub_dir, "temp")
                    coverage_path = os.path.join(temp_dir, "coverage.xml")
                    if os.path.exists(temp_dir):
                        for file_name in os.listdir(temp_dir):
                            if file_name.endswith(".java"):
                                all_java_files_cnt += 1
                                break
                    coverage_json = os.path.join(temp_dir, "coverage.json")
                    if os.path.exists(coverage_json):
                        success_cnt_json += 1

                    json_file_number = len(os.listdir(sub_dir)) - 1
                    if os.path.exists(coverage_path):
                        success_cnt += 1
                        if json_file_number > 3:
                            repair_success_cnt += 1
                            repair_rounds[math.ceil(json_file_number / 3)] += 1
                    else:
                        fail_cnt += 1
                        if json_file_number > 3:
                            repair_failed_cnt += 1
    print("Project name:        " + str(project_name))
    print("All files:           " + str(all_files_cnt))
    print("All java files:      " + str(all_java_files_cnt))
    print("Success:             " + str(success_cnt))
    print("Success json:        " + str(success_cnt_json))
    print("Fail:                " + str(fail_cnt))
    print("Repair success:      " + str(repair_success_cnt))
    print("Repair failed:       " + str(repair_failed_cnt))
    print("Repair rounds:       " + str(repair_rounds))
    print("runtemp counts:      " + str(runtemp_cnt))
    print()


def full_analysis(directory=result_dir):
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            if dir_name.startswith("scope_test"):
                result_analysis(os.path.join(root, dir_name))


if __name__ == '__main__':
    # result_analysis()
    full_analysis("")
    # get_numberutils_result()
