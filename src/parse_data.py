"""
This file is for parsing the .json data.
And insert them into Current Database.

Author: Xie zhuokui
Date: 2023-04-01
"""

import json
import os
from database import database


def parse_data(dir_path: str):
    """
    Parse the data from .json files.
    :param dir_path: the path of the .json files.
    :return: None
    """
    db = database()
    for root, dirs, files in os.walk(dir_path):
        for filename in files:
            if filename.endswith('.json'):
                with open(os.path.join(root, filename), "r") as f:
                    json_data = json.load(f)

                for class_data in json_data:
                    # Get class data
                    project_name = class_data['project_name']
                    class_name = class_data['class_name']
                    class_path = class_data['class_path']
                    c_sig = class_data['c_sig']

                    if class_data['superclass']:
                        super_class = class_data['superclass'].split(' ')[1]
                    else:
                        super_class = ""

                    if class_data['imports']:
                        imports = "\n".join(class_data['imports'])
                    else:
                        imports = ""

                    if "package" in class_data:
                        package = class_data["package"]
                    else:
                        package = ""

                    has_constructor = class_data['has_constructor']

                    # Get field data
                    fields = []
                    for field in class_data['fields']:
                        if field['original_string'] not in fields:
                            fields.append(field['original_string'])
                    fields = "\n".join(fields)

                    # Will append from all constructors
                    c_deps = {}

                    # Get method data
                    methods = class_data['methods']
                    for method_data in methods:
                        m_sig = method_data['m_sig']
                        method_name = method_data['method_name']
                        source_code = method_data['source_code']
                        use_field = method_data['use_field']
                        parameters = method_data['parameters']
                        if "public" in method_data['modifiers']:
                            is_public = True
                        else:
                            is_public = False
                        is_constructor = method_data['is_constructor']
                        is_get_set = method_data['is_get_set']
                        m_deps = method_data['m_deps']

                        # Add dependencies from constructor
                        if is_constructor:
                            for dep_class in m_deps:
                                if dep_class not in c_deps:
                                    c_deps[dep_class] = []
                                c_deps[dep_class].append(m_deps[dep_class])

                        # insert method data into table method
                        db.insert("method", row={"project_name": project_name,
                                                 "signature": m_sig,
                                                 "method_name": method_name,
                                                 "parameters": parameters,
                                                 "source_code": source_code,
                                                 "class_name": class_name,
                                                 "dependencies": str(m_deps),
                                                 "use_field": use_field,
                                                 "is_constructor": is_constructor,
                                                 "is_get_set": is_get_set,
                                                 "is_public": is_public})

                    # insert class data into table class
                    db.insert("class", row={"project_name": project_name,
                                            "class_name": class_name,
                                            "class_path": class_path,
                                            "signature": c_sig,
                                            "super_class": super_class,
                                            "package": package,
                                            "imports": imports,
                                            "fields": fields,
                                            "has_constructor": has_constructor,
                                            "dependencies": str(c_deps)})
                    print(class_name, "FINISHED!")


if __name__ == '__main__':
    print("This action will alter the information in database.")
    confirm = input("Are you sure to parse the data? (y/n) ")
    if confirm == "y":
        parse_data("/Users/chenyi/Desktop/ChatTester/TestGPT_ASE/information/Lang")
    else:
        print("Canceled.")
