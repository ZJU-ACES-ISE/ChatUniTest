"""
This file is for exporting the data from database.
And save them into .txt files.
Noting that this file will need some modification in the future.
Author: Xie zhuokui
Date: 2023-04-01
"""

import os
import json
from database import database

dataset_path = "../dataset/"
db = database()


def gen_file_name(method_id, project_name, class_name, method_name, direction):
    if direction == "raw":
        return str(method_id) + "%" + project_name + "%" + class_name + "%" + method_name + "%raw.json"
    return str(method_id) + "%" + project_name + "%" + class_name + "%" + method_name + "%d" + str(
        direction) + ".json"


def create_dataset_dirs():
    def _create_folder(dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    _create_folder(dataset_path)
    _create_folder(os.path.join(dataset_path, "direction_1"))
    _create_folder(os.path.join(dataset_path, "direction_3"))
    _create_folder(os.path.join(dataset_path, "raw_data"))


def export_data():
    """
    Export data from database.
    :return: None
    """
    create_dataset_dirs()
    # Get the data from database.
    sql_query = "SELECT COUNT(*) FROM method;"
    method_n = db.select(script=sql_query)[0][0]
    for method_id in range(1, method_n + 1):
        row = db.select(table_name="method",
                        conditions={"id": method_id},
                        result_cols=["project_name", "signature", "method_name", "parameters", "source_code",
                                     "class_name", "dependencies", "use_field", "is_constructor", "is_get_set",
                                     "is_public"])
        if row:
            project_name, m_sig, method_name, parameters, source_code, class_name, m_deps, use_field, is_constructor, \
                is_get_set, is_public = row[0]

            if isinstance(m_deps, str):
                m_deps = eval(m_deps)

            # Get class data
            class_row = db.select(table_name="class",
                                  conditions={"project_name": project_name, "class_name": class_name},
                                  result_cols=["class_path", "signature", "super_class", "package", "imports",
                                               "fields", "has_constructor", "dependencies"])
            class_path, c_sig, super_class, package, imports, fields, has_constructor, c_deps = class_row[0]

            if isinstance(c_deps, str):
                c_deps = eval(c_deps)
                c_deps = list(set(c_deps))

            # Direction 1: imports + fc + c + f + fm + m
            json_data = {"focal_method": method_name, "class_name": class_name, "information": ""}
            direction_1 = ""
            if package:
                direction_1 += package + "\n" + "\n"
            if imports:  # imports
                direction_1 += imports + "\n"
            if c_sig:  # c
                direction_1 += c_sig + "{\n"

            # Add fm
            direction_1 += source_code + "\n"

            if fields:  # f
                direction_1 += fields + "\n"

            # Merge all methods
            methods = [x[0] for x in db.select(table_name="method",
                                               conditions={"class_name": class_name,
                                                           "project_name": project_name},
                                               result_cols=["signature"])]
            methods.remove(m_sig)
            methods = "\n".join(methods)
            direction_1 += methods + "\n}"

            json_data["information"] = direction_1
            save_name = gen_file_name(method_id, project_name, class_name, method_name, 1)
            with open(os.path.join(dataset_path, "direction_1", save_name), "w") as f:
                json.dump(json_data, f)
            print(save_name, "success!")

            # Direction 3: imports + fc + c + f + fm + m
            # AND + c_deps + m_deps
            direction_3 = {"c_deps": {}, "m_deps": {}, "full_fm": "", "focal_method": m_sig,
                           "class_name": class_name}

            other_methods_list = []
            if "this" in m_deps:  # Get the methods(parameters) in same class
                for method in m_deps["this"]:
                    if method not in other_methods_list:
                        other_methods_list.append(method)

            # Generate full context for focal method
            direction_3["full_fm"] = gen_full_context(project_name, class_name, method_id, other_methods_list)

            # Generate detailed relative signatures for method's dependencies
            for dep in m_deps:
                if dep not in direction_3["m_deps"]:
                    if class_in_project(dep, project_name):
                        direction_3["m_deps"][dep] = gen_required_sigs(project_name, dep, m_deps[dep])

            # Generate constructor's information for class's dependencies
            for dep in c_deps:
                # Exclude class existed in m_deps, because they are already processed above.
                if dep not in direction_3["c_deps"] and dep not in direction_3["m_deps"]:
                    if class_in_project(dep, project_name):
                        direction_3["c_deps"][dep] = gen_min_sigs(project_name, dep)

            save_name = gen_file_name(method_id, project_name, class_name, method_name, 3)
            with open(os.path.join(dataset_path, "direction_3", save_name), "w") as f:
                json.dump(direction_3, f)
            print(save_name, "success!")

            raw_data = {
                "id": method_id,
                "project_name": project_name,
                "signature": m_sig,
                "method_name": method_name,
                "parameters": parameters,
                "source_code": source_code,
                "class_name": class_name,
                "dependencies": m_deps,
                "use_field": use_field,
                "is_constructor": is_constructor,
                "is_get_set": is_get_set,
                "is_public": is_public,
                "package": package,
                "imports": imports
            }
            save_name = gen_file_name(method_id, project_name, class_name, method_name, "raw")
            with open(os.path.join(dataset_path, "raw_data", save_name), "w") as f:
                json.dump(raw_data, f)
            print(save_name, "success!")


def gen_min_sigs(project_name: str, class_name: str) -> str:
    """
    Generate min sigs for a class. S_fc and S_c
    :param project_name:
    :param class_name:
    :return:
    """
    class_row = db.select(table_name="class",
                          conditions={"project_name": project_name, "class_name": class_name},
                          result_cols=["signature", "fields"])
    if not class_row:
        raise RuntimeError("Error happened in function gen_min_sigs.")

    # Get class information
    c_sig, fields = class_row[0]

    # Prepare full text and fields information
    full_text = c_sig + "{\n"
    full_text += fields + "\n"

    # Get constructor information
    constructors = db.select(table_name="method",
                             conditions={"class_name": class_name,
                                         "is_constructor": True,
                                         "project_name": project_name},
                             result_cols=["signature"])

    for constructor in constructors:
        full_text += constructor[0] + "\n"

    full_text += "\n}"
    return full_text


def gen_required_sigs(project_name: str, class_name: str, methods_list: list):
    """
    Generate required sigs for a list of methods. Specially for m_deps.
    :param project_name:
    :param class_name:
    :param methods_list:
    :return:
    """
    full_text = ""
    class_row = db.select(table_name="class",
                          conditions={"project_name": project_name, "class_name": class_name},
                          result_cols=["signature", "fields", "has_constructor"])
    if not class_row:
        raise RuntimeError("Error happened in function gen_required_sigs")

    # Get the class information
    c_sig, fields, has_constructor = class_row[0]

    # prepare class signature and fields data
    full_text += c_sig + "\n" + fields + "\n"

    # prepare getter and setter's signatures
    gs_sigs = db.select(table_name="method",
                        conditions={"project_name": project_name, "class_name": class_name,
                                    "is_get_set": True}, result_cols=["signature"])
    for gs in gs_sigs:
        full_text += gs[0] + "\n"

    # prepare constructors' signatures
    constructors = db.select(table_name="method",
                             conditions={"project_name": project_name, "class_name": class_name,
                                         "is_constructor": True}, result_cols=["signature"])
    for cons in constructors:
        full_text += cons[0] + "\n"

    # prepare methods' signatures
    for parameters in methods_list:
        m_sig = db.select(table_name="method",
                          conditions={"project_name": project_name,
                                      "class_name": class_name,
                                      "parameters": parameters},
                          result_cols=["signature"])
        for sig in m_sig:
            full_text += sig[0] + "\n"

    full_text += "\n}"
    return full_text


def gen_full_sigs(project_name: str, class_name: str) -> str:
    """
    Generate full sigs for a class.
    :param project_name:
    :param class_name:
    :return:
    """
    # Get class data
    class_row = db.select(table_name="class",
                          conditions={"project_name": project_name, "class_name": class_name},
                          result_cols=["class_path", "signature", "super_class", "imports",
                                       "fields", "has_constructor", "dependencies"])
    if not class_row:
        raise RuntimeError("Error happened in gen_full_sigs.")

    class_path, c_sig, super_class, imports, fields, has_constructor, c_deps = class_row[0]

    full_text = c_sig + "{\n"
    full_text += fields + "\n"

    methods = db.select(table_name="method",
                        conditions={"class_name": class_name,
                                    "project_name": project_name},
                        result_cols=["signature"])

    for method in methods:
        full_text += method[0] + "\n"

    full_text += "\n}"
    return full_text


def gen_full_context(project_name: str, class_name: str, method_id: int, dep_methods: list,
                     add_imports=True) -> str:
    """
    Generate full context for focal methods.
    :param method_id:
    :param add_imports:
    :param project_name:
    :param class_name:
    :param dep_methods:
    :return:
    """

    # Get class data
    class_row = db.select(table_name="class",
                          conditions={"project_name": project_name, "class_name": class_name},
                          result_cols=["class_path", "signature", "super_class", "package", "imports",
                                       "fields", "has_constructor", "dependencies"])
    if not class_row:
        raise RuntimeError("Error happened in gen_full_context.")
    class_path, c_sig, super_class, package, imports, fields, has_constructor, c_deps = class_row[0]

    fm_code = ""
    use_field = False
    row = db.select(table_name="method",
                    conditions={"project_name": project_name, "class_name": class_name,
                                "id": method_id},
                    result_cols=["use_field", "source_code"])
    if not row:
        raise RuntimeError("Error happened in gen_full_context.")
    if row[0][0]:
        use_field = True
    fm_code += row[0][1] + "\n"
    for dep in dep_methods:  # Judge if focal methods use field
        rows = db.select(table_name="method",
                         conditions={"project_name": project_name, "class_name": class_name,
                                     "parameters": dep},
                         result_cols=["use_field", "signature"])
        for row in rows:  # There may be function with same names
            if row[0]:
                use_field = True
            fm_code += row[1] + "\n"

    full_text = ""
    if add_imports:
        if package:
            full_text += package + "\n" + "\n"
        full_text += imports + "\n"
    full_text += c_sig + "{\n"

    if has_constructor:  # Add constructor if focal methods use field
        constructors = db.select(table_name="method",
                                 conditions={"class_name": class_name,
                                             "is_constructor": True,
                                             "project_name": project_name},
                                 result_cols=["signature"])
        for constructor in constructors:
            full_text += constructor[0] + "\n"

    if use_field and fields:  # Add fields if focal methods use field
        full_text += fields + "\n"
        methods = db.select(table_name="method",
                            conditions={"class_name": class_name,
                                        "is_get_set": True,
                                        "project_name": project_name},
                            result_cols=["signature"])
        for method in methods:
            full_text += method[0] + "\n"

    full_text += fm_code + "}"

    return full_text


def class_in_project(class_name: str, project_name: str):
    """
    Check if the class is in the project.
    :param class_name: the class name
    :param project_name: the project name
    :return: True if the class is in the project.
    """
    row = db.select(table_name="class",
                    conditions={"class_name": class_name,
                                "project_name": project_name},
                    result_cols=["class_path"])
    if row:
        return True
    return False


if __name__ == '__main__':
    export_data()
