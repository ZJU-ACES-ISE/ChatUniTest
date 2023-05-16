"""
This file is for starting a scope test for selected methods.
It will automatically create a new folder inside dataset as well as result folder.
The folder format is "scope_test_YYYYMMDDHHMMSS_Direction".
The dataset folder will contain all the information in the direction.
"""
import os
import datetime
import re
import subprocess
import time

from config import *
from tools import *
from askGPT import start_generation, start_whole_process, extract_and_run
from database import database
from run_test_case.run_test_cases import start_run
from parse_xml import result_analysis

db = database()


def create_dataset_result_folder(direction):
    """
    Create a new folder for this scope test.
    :param direction: The direction of this scope test.
    :return: The path of the new folder.
    """
    # Get current time
    now = datetime.datetime.now()
    # format the time as a string
    time_str = now.strftime("%Y%m%d%H%M%S")
    # Create the folder
    dataset_path = os.path.join(dataset_dir, "scope_test%" + time_str + "%" + direction)
    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)
    else:
        raise Exception("Dataset folder already exists.")
    result_path = os.path.join(result_dir, "scope_test%" + time_str + "%" + direction)
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    else:
        raise Exception("Result folder already exists.")
    return dataset_path, result_path


def create_new_folder(folder_path: str):
    """
    Create a new folder.
    :param folder_path: The folder path.
    :return: None
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        raise Exception("Folder already exists.")


def copy_files_to_folder(file_list: list, src_dir: str, dst_dir: str):
    """
    Copy the files to the folder.
    :param raw_data: database data
    :param dst_dir: destination directory
    :param src_dir: source directory
    :param file_list: The file list to copy.
    :return: None
    """
    for file in file_list:
        src_path = os.path.join(src_dir, file)
        new_folder_path = os.path.join(dst_dir, file.split(".")[0])
        create_new_folder(new_folder_path)
        dst_path = os.path.join(new_folder_path, file)
        if not os.path.exists(src_path):
            raise Exception("File " + file + " does not exist.")
        if os.path.exists(dst_path):
            raise Exception("File " + file + " already exists.")
        os.system("cp " + src_path + " " + dst_path)
        # subprocess.call(['cp', src_path, dst_path])


def find_all_files(folder_path: str, method_ids: list = None):
    """
    Find all the files in the folder.
    :param method_ids: The method ids need to be found.
    :param folder_path: The folder path.
    :return: The file list.
    """
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.split("%")[0] not in method_ids:
                continue
            file_list.append(file)
    return file_list


def start_scope_test(sql_query: str, template_file: str):
    """
    Start the scope test.
    :param sql_query:
    :param template_file:
    :return:
    """
    method_ids = [x[0] for x in db.select(script=sql_query)]
    if method_ids is None:
        raise Exception("Method ids cannot be None.")
    if not isinstance(method_ids[0], str):
        method_ids = [str(i) for i in method_ids]

    direction = template_file.split("_")[0]
    print("The following methods will be tested: " + str(method_ids) + ".")
    print("The direction is " + str(direction) + ".")
    print("The approximate cost will be $", len(method_ids) * 0.0027 * test_number, ".")
    confirm = input("Are you sure to start the scope test? (y/n): ")
    if confirm != "y":
        print("Scope test cancelled.")
        return

    # Create the new folder
    dataset_path, result_path = create_dataset_result_folder(template_file.split(".")[0])

    # Find all the files
    source_dir = os.path.join(dataset_dir, "direction_" + str(direction[1:]))
    file_list = find_all_files(source_dir, method_ids)

    # Copy the files to the folder
    copy_files_to_folder(file_list, source_dir, dataset_path)
    start_generation(dataset_path, template_file, result_path)


def start_scope_test_repair(sql_query: str, threaded=True, repair=True, confirmed=False):
    """
    Start the scope test.
    :param threaded:
    :param repair:
    :param sql_query:
    :return:
    """
    match = re.search(r"project_name\s*=\s*'([\w-]*)'", sql_query)
    if match:
        project_name = match.group(1)
        print(project_name)
    else:
        raise RuntimeError("One project at one time.")
    # delete the old result
    remove_single_test_output_dirs(get_project_abspath(project_name))

    method_ids = [x[0] for x in db.select(script=sql_query)]
    if not method_ids:
        raise Exception("Method ids cannot be None.")
    if not isinstance(method_ids[0], str):
        method_ids = [str(i) for i in method_ids]
    print("You are about to start the whole process of scope test.")
    print("The following methods will be tested: " + str(method_ids) + ".")
    print("The approximate cost will be $", len(method_ids) * 0.0027 * test_number, ".")
    record = "This is a record of a scope test.\n"
    if not confirmed:
        confirm = input("Are you sure to start the scope test? (y/n): ")
        if confirm != "y":
            print("Scope test cancelled.")
            return
        confirm = input("State your purpose of this scope test: ")
        record += "Scope test purpose: " + confirm + "\n"

    # Create the new folder
    dataset_path, result_path = create_dataset_result_folder("")

    record += "Dataset path: " + dataset_path + "\n"
    record += "Result path: " + result_path + "\n"
    record += 'SQL script: "' + sql_query + '"\n'
    record += "Included methods: " + str(method_ids) + "\n"

    record_path = os.path.join(result_path, "record.txt")
    with open(record_path, "w") as f:
        f.write(record)
    print("The record has been saved at", record_path)

    # Find all the files
    source_dir = os.path.join(dataset_dir, "direction_1")
    file_list = find_all_files(source_dir, method_ids)

    # Copy the files to the folder
    copy_files_to_folder(file_list, source_dir, dataset_path)
    start_whole_process(dataset_path, threaded=threaded, repair=repair)
    print("WHOLE PROCESS FINISHED")
    # Run accumulated tests
    project_path = os.path.abspath(os.path.join(projects_dir, project_name))
    print("START ALL TESTS")

    start_run(result_path, project_path) #TODO
    # Todo save whole test result
    try:
        with open(record_path, "a") as f:
            f.write("Whole test result at: " + find_result_in_projects() + "\n")
    except Exception as e:
        print("Cannot save whole test result.")
        print(e)

    print("SCOPE TEST FINISHED")


if __name__ == '__main__':
    # # TODO: directly run all tests from a source on a project
    # test_cases_src = '/root/TestGPT_ASE/result/scope_test%20230504204223%'
    # target_dir = '/root/TestGPT_ASE/projects/kyrestia'
    # total_compile, total_test_run = start_run(test_cases_src, target_dir)
    # exit()

    # TODO: use new projects jinja template, checkout java version to 11
    sql_query = "SELECT id FROM method WHERE project_name='event-ruler';"
    start_scope_test_repair(sql_query, threaded=True, repair=True, confirmed=False)
    exit()


    # sql_query = "SELECT DISTINCT project_name FROM method WHERE project_name like 'Lang_%';"

    # TODO: d4j projects jinja template, checkout java version to 11
    Lang = [
        'Lang_26_f', 'Lang_3_f', 'Lang_45_f', 'Lang_27_f', 'Lang_39_f', 'Lang_59_f', 'Lang_14_f', 'Lang_32_f',
        'Lang_40_f', 'Lang_41_f', 'Lang_63_f', 'Lang_20_f', 'Lang_16_f', 'Lang_17_f', 'Lang_56_f', 'Lang_36_f',
        'Lang_33_f', 'Lang_46_f', 'Lang_4_f', 'Lang_38_f', 'Lang_44_f', 'Lang_1_f', 'Lang_53_f', 'Lang_11_f',
        'Lang_61_f', 'Lang_54_f', 'Lang_9_f', 'Lang_13_f', 'Lang_6_f', 'Lang_19_f', 'Lang_60_f', 'Lang_18_f',
        'Lang_48_f', 'Lang_65_f', 'Lang_29_f', 'Lang_37_f', 'Lang_15_f', 'Lang_52_f', 'Lang_30_f', 'Lang_58_f',
        'Lang_24_f', 'Lang_47_f', 'Lang_49_f', 'Lang_51_f', 'Lang_28_f', 'Lang_34_f', 'Lang_10_f', 'Lang_55_f',
        'Lang_23_f', 'Lang_64_f', 'Lang_12_f', 'Lang_5_f', 'Lang_8_f', 'Lang_21_f', 'Lang_31_f', 'Lang_50_f',
        'Lang_7_f', 'Lang_57_f', 'Lang_35_f', 'Lang_22_f', 'Lang_43_f'
    ]
    Chart = [
        'Chart_13_f', 'Chart_21_f', 'Chart_14_f',
        'Chart_7_f', 'Chart_17_f', 'Chart_10_f', 'Chart_24_f', 'Chart_19_f','Chart_1_f', 'Chart_9_f', 'Chart_25_f',
        'Chart_22_f', 'Chart_12_f', 'Chart_26_f', 'Chart_3_f', 'Chart_6_f','Chart_8_f', 'Chart_15_f', 'Chart_11_f',
        'Chart_23_f', 'Chart_2_f', 'Chart_4_f', 'Chart_20_f', 'Chart_16_f', 'Chart_5_f', 'Chart_18_f'
    ]
    Cli = [
        'Cli_12_f',
        'Cli_3_f', 'Cli_23_f', 'Cli_29_f', 'Cli_37_f', 'Cli_15_f', 'Cli_27_f', 'Cli_10_f', 'Cli_8_f',
        'Cli_25_f', 'Cli_28_f', 'Cli_11_f', 'Cli_7_f', 'Cli_40_f', 'Cli_33_f', 'Cli_17_f', 'Cli_26_f',
        'Cli_31_f', 'Cli_18_f', 'Cli_20_f', 'Cli_16_f', 'Cli_39_f', 'Cli_36_f', 'Cli_14_f', 'Cli_34_f',
        'Cli_4_f', 'Cli_13_f', 'Cli_1_f', 'Cli_38_f', 'Cli_19_f', 'Cli_22_f', 'Cli_30_f', 'Cli_32_f',
        'Cli_21_f', 'Cli_5_f', 'Cli_2_f', 'Cli_35_f', 'Cli_24_f', 'Cli_9_f'
    ]
    Csv = [
        'Csv_10_f', 'Csv_2_f',
        'Csv_8_f', 'Csv_14_f', 'Csv_11_f', 'Csv_9_f', 'Csv_12_f', 'Csv_16_f', 'Csv_4_f', 'Csv_6_f',
        'Csv_7_f', 'Csv_3_f', 'Csv_13_f', 'Csv_5_f', 'Csv_15_f', 'Csv_1_f'
    ]
    Gson = [
        'Gson_9_f', 'Gson_2_f',
        'Gson_4_f', 'Gson_7_f', 'Gson_3_f', 'Gson_18_f', 'Gson_12_f', 'Gson_10_f', 'Gson_8_f', 'Gson_11_f',
        'Gson_1_f', 'Gson_14_f', 'Gson_13_f', 'Gson_16_f', 'Gson_6_f', 'Gson_5_f', 'Gson_17_f', 'Gson_15_f'
    ]

    combined_lists = Lang + Chart + Cli + Csv + Gson
    total_length = len(combined_lists)
    new_list_length = total_length // 5

    # server task assignments
    a_1 = combined_lists[:new_list_length]
    a_2 = combined_lists[new_list_length: new_list_length * 2]
    a_3 = combined_lists[new_list_length * 2: new_list_length * 3]
    a_4 = combined_lists[new_list_length * 3: new_list_length * 4]
    a_5 = combined_lists[new_list_length * 4:]

    a_1 = ['Lang_39_f', 'Lang_59_f', 'Lang_14_f', 'Lang_32_f', 'Lang_40_f', 'Lang_41_f', 'Lang_63_f', 'Lang_20_f', 'Lang_16_f', 'Lang_17_f', 'Lang_56_f', 'Lang_36_f', 'Lang_33_f', 'Lang_46_f', 'Lang_4_f', 'Lang_38_f', 'Lang_44_f', 'Lang_1_f', 'Lang_53_f', 'Lang_11_f', 'Lang_61_f', 'Lang_54_f', 'Lang_9_f', 'Lang_13_f', 'Lang_6_f', 'Lang_19_f', 'Lang_60_f', 'Lang_18_f']
    # a_2 = ['Lang_30_f', 'Lang_58_f', 'Lang_24_f', 'Lang_47_f', 'Lang_49_f', 'Lang_51_f', 'Lang_28_f', 'Lang_34_f', 'Lang_10_f', 'Lang_55_f', 'Lang_23_f', 'Lang_64_f', 'Lang_12_f', 'Lang_5_f', 'Lang_8_f', 'Lang_21_f', 'Lang_31_f', 'Lang_50_f', 'Lang_7_f', 'Lang_57_f', 'Lang_35_f', 'Lang_22_f', 'Lang_43_f', 'Chart_13_f', 'Chart_21_f', 'Chart_14_f']
    a_2 = ['Lang_30_f', 'Lang_58_f', 'Lang_24_f', 'Lang_47_f', 'Lang_49_f', 'Lang_51_f', 'Lang_28_f', 'Lang_34_f', 'Lang_10_f', 'Lang_55_f', 'Lang_23_f', 'Lang_64_f', 'Lang_12_f', 'Lang_5_f', 'Lang_8_f']
    a_3 = ['Chart_1_f', 'Chart_9_f', 'Chart_25_f', 'Chart_22_f', 'Chart_12_f', 'Chart_26_f', 'Chart_3_f', 'Chart_6_f', 'Chart_8_f', 'Chart_15_f', 'Chart_11_f', 'Chart_23_f', 'Chart_2_f', 'Chart_4_f', 'Chart_20_f', 'Chart_16_f', 'Chart_5_f', 'Chart_18_f', 'Cli_12_f', 'Cli_3_f', 'Cli_23_f', 'Cli_29_f', 'Cli_37_f', 'Cli_15_f', 'Cli_27_f', 'Cli_10_f', 'Cli_8_f']
    # a_4 = ['Cli_31_f', 'Cli_18_f', 'Cli_20_f', 'Cli_16_f', 'Cli_39_f', 'Cli_36_f', 'Cli_14_f', 'Cli_34_f', 'Cli_4_f', 'Cli_13_f', 'Cli_1_f', 'Cli_38_f', 'Cli_19_f', 'Cli_22_f', 'Cli_30_f', 'Cli_32_f', 'Cli_21_f', 'Cli_5_f', 'Cli_2_f', 'Cli_35_f', 'Cli_24_f', 'Cli_9_f', 'Csv_10_f', 'Csv_2_f']
    a_4 = ['Lang_21_f', 'Lang_31_f', 'Lang_50_f', 'Lang_7_f', 'Lang_57_f', 'Lang_35_f', 'Lang_22_f', 'Lang_43_f', 'Chart_13_f', 'Chart_21_f', 'Chart_14_f']
    # a_5 = ['Csv_15_f', 'Csv_1_f', 'Gson_9_f', 'Gson_2_f', 'Gson_4_f', 'Gson_7_f', 'Gson_3_f', 'Gson_18_f', 'Gson_12_f', 'Gson_10_f', 'Gson_8_f', 'Gson_11_f', 'Gson_1_f', 'Gson_14_f', 'Gson_13_f', 'Gson_16_f', 'Gson_6_f', 'Gson_5_f', 'Gson_17_f', 'Gson_15_f']
    a_5 = ['Cli_10_f', 'Cli_8_f']
    # projects = [x[0] for x in db.select(script=sql_query)]

    # choose the server to run task
    # TODO: d4j projects jinja template, checkout java version to 11
    projects = a_5

    for p in projects:
        print("Generate tests for:", projects)
        print("Now:", p)

        sql_query = "SELECT * FROM method WHERE project_name='" + p + "' and is_public IS TRUE and is_constructor IS FALSE;"
        try:
            start_scope_test_repair(sql_query, threaded=True, repair=True, confirmed=True)
            result_analysis()
        except Exception as e:
            print(e)
        time.sleep(15)

