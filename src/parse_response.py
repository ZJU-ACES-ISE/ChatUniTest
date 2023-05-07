import os
import json
import glob
import sys
import re
from tools import *

REPAIR_PACKAGES = 0
REPAIR_IMPORTS = 0


def get_code(response):
    '''
    Get code in the response.
    '''
    content = response['choices'][0]['message']['content']
    code = re.search(r"```[Jjava]*([\s\S]*?)```", content)
    if code:
        # Append the extracted test case to the Java file
        method_test_case = code.group(1).strip('\n')
        return method_test_case
    else:
        print("Invalid test case format!")
        return ''


def repair_package(code, package_info):
    '''
    Repair package declaration in test.
    '''
    global REPAIR_PACKAGES
    first_line = code.split('import')[0]
    if package_info == '' or package_info in first_line:
        return code
    REPAIR_PACKAGES += 1
    code = package_info + "\n" + code
    return code


# TODO: imports can be optimized
def repair_imports(code, imports):
    '''
    Repair imports in test.
    '''
    global REPAIR_IMPORTS
    import_list = imports.split('\n')
    first_line, _code = code.split('\n', 1)
    for _import in reversed(import_list):
        if _import not in code:
            REPAIR_IMPORTS += 1
            _code = _import + "\n" + _code
    return first_line + '\n' + _code


def add_timeout(test_case, timeout=8000):
    '''
    Add timeout to test cases. Only for Junit 5
    '''
    # check junit version
    junit4 = 'import org.junit.Test'
    junit5 = 'import org.junit.jupiter.api.Test'
    if junit4 in test_case: # Junit 4
        test_case = test_case.replace('@Test(', f'@Test(timeout = {timeout}, ')
        return test_case.replace('@Test\n', f'@Test(timeout = {timeout})\n')
    elif junit5 in test_case: # Junit 5
        timeOutImport = 'import org.junit.jupiter.api.Timeout;'
        test_case = repair_imports(test_case, timeOutImport)
        return test_case.replace('@Test\n', f'@Test\n    @Timeout({timeout})\n')
    else:
        print("Can not know which junit version!")
        return test_case


def export_method_test_case(output, class_name, m_id, test_num, method_test_case):
    '''
    Export test case to file.
    output : pathto/project/testcase.java
    '''
    method_test_case = add_timeout(method_test_case)
    f = os.path.join(output, class_name + "_" + str(m_id) + '_' + str(test_num) + "Test.java")
    if not os.path.exists(output):
        os.makedirs(output)
    with open(f, "w") as output_file:
        output_file.write(method_test_case)


def change_class_name(test_case, class_name, m_id, test_num):
    '''
    Change the class name in the test_case by given m_id.
    '''
    old_name = class_name + 'Test'
    new_name = class_name + '_' + str(m_id) + '_' + str(test_num) + 'Test'
    return test_case.replace(old_name, new_name, 1)


def process_response_file(filepath, output):
    '''
    Process response.
    :return: stantard test case file.
    '''
    filename = os.path.basename(filepath)
    with open(filepath, 'r') as f:
        response = json.load(f)

    # m_id, project_name, class_name, method_name, direction, test_num = filename.split('_')
    m_id, project_name, class_name, method_name, direction, test_num = parse_file_name(filename)
    # output =  os.path.join(output, project_name)

    package_info, imports = get_project_class_info(m_id, project_name, class_name, method_name)
    code = get_code(response)
    if code == '':
        return False
    test_case = repair_package(code, package_info)
    test_case = repair_imports(test_case, imports)
    export_method_test_case(output, class_name, m_id, test_num,
                            change_class_name(test_case, class_name, m_id, test_num))
    return True


def start_process(directory):
    directory = directory.rstrip('/')

    # output = '/data/share/data/data_parsed/'
    # output = os.path.join(output, directory.split('/')[-2], directory.split('/')[-1])

    os.chdir(directory)
    files = glob.glob("**/*.json", recursive=True)
    total_num = len(files)
    success_num = 0
    for file in files:
        # print("processing: ", file)
        filepath = os.path.join(directory, file)
        file_output = os.path.dirname(filepath)
        if process_response_file(filepath, file_output):
            success_num += 1
    print("Total files: ", total_num)
    print("Success parsed files: ", success_num)
    print("Total repair packages: ", REPAIR_PACKAGES)
    print("Total repair imports: ", REPAIR_IMPORTS)
    return directory


if __name__ == '__main__':
    directory = '/data/share/TestGPT_ASE/result/scope_test%20230414210027%d3_2'
    start_process(directory)
