import os.path
import time

from tools import *
from database import *
from parse_data import parse_data
from export_data import export_data
from scope_test import start_generation
from parse_xml import result_analysis
from task import Task


def clear_dataset():
    """
    Clear the dataset folder.
    :return: None
    """
    # Delete the dataset folder
    if os.path.exists(dataset_dir):
        shutil.rmtree(dataset_dir)


def run():
    """
    Generate the test cases with one-click.
    :return: None
    """
    # Delete history data
    drop_table()

    # Create the table
    create_table()

    # Parse project
    info_path = Task.parse(project_dir)

    # Parse data
    parse_data(info_path)

    # clear last dataset
    clear_dataset()

    # Export data for multi-process
    export_data()

    project_name = os.path.basename(os.path.normpath(project_dir))

    # Modify SQL query to test the designated classes.
    sql_query = """
        SELECT id FROM method WHERE project_name='{}';
    """.format(project_name)

    # Start the whole process
    start_generation(sql_query, multiprocess=False, repair=True, confirmed=False)

    # Export the result
    result_analysis()


if __name__ == '__main__':
    print("Make sure the config.ini is correctly configured.")
    seconds = 5
    while seconds > 0:
        print(seconds)
        time.sleep(1)  # Pause for 1 second
        seconds -= 1
    run()
