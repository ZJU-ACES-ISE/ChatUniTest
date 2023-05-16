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
from Task import Task

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

    # start_run(result_path, project_path)
    Task.all_test(result_path, project_path)
    # Todo save whole test result
    try:
        with open(record_path, "a") as f:
            f.write("Whole test result at: " + find_result_in_projects() + "\n")
    except Exception as e:
        print("Cannot save whole test result.")
        print(e)

    print("SCOPE TEST FINISHED")


if __name__ == '__main__':
    # TODO: use new projects jinja template, checkout java version to 11
    # Task.parse("../projects/Lang_1_f")
    # exit()

    sql_query = "SELECT id FROM method WHERE project_name='Lang_1_f' AND class_name='NumberUtils' LIMIT 1;"
    start_scope_test_repair(sql_query, threaded=False, repair=True, confirmed=False)
    exit()