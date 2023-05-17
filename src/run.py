import os.path
import time

from tools import *
from database import *
from parse_data import parse_data
from export_data import export_data
from scope_test import start_generation
from parse_xml import result_analysis


def run():
    """
    Generate the test cases with one-click.
    :return: None
    """
    # Delete history data
    drop_table()

    # Create the table
    create_table()

    # Parse data
    parse_data(project_dir)

    # Export data for multi-process
    export_data()

    # Start the whole process
    project_name = os.path.basename(os.path.normpath(project_dir))
    start_generation(project_name=project_name, multiprocess=True, repair=True, confirmed=False)

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
