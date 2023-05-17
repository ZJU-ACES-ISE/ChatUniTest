import mysql.connector
from config import config
import warnings


class database(object):
    def __init__(self):
        self.host = config.get("database", "host")
        self.user = config.get("database", "user")
        self.password = config.get("database", "password")
        self.database = config.get("database", "database")
        if config.has_option("database", "port"):
            self.port = config.get("database", "port")
        else:
            self.port = 3306
        self.db = None
        self.cursor = None
        self.connect()

    def connect(self):
        """
        Establish a connection to the MySQL database
        :return:
        """
        self.db = mysql.connector.connect(
            host=self.host,
            user=self.user,
            port=self.port,
            password=self.password,
            database=self.database
        )
        self.cursor = self.db.cursor()

    def execute(self, script):
        if script is None:
            return
        if self.db is None:
            self.connect()
        self.cursor.execute(script)

    def select(self, table_name: str = "", conditions=None, result_cols: (str, list) = "*", script=None):
        if self.db is None:
            self.connect()
        if script is None:
            if table_name == "":
                raise RuntimeError("if script is not provided, table_name is required.")
            # Generate the SELECT statement
            if isinstance(result_cols, list):
                result_cols = ", ".join(result_cols)

            script = r"SELECT {} FROM {}".format(result_cols, table_name)
            if conditions is not None:
                script += " WHERE"
                # Add the WHERE clause using the dictionary values
                for key, value in conditions.items():
                    if value is None:
                        script += " {} is %s AND".format(key)
                    else:
                        script += " {} = %s AND".format(key)
                script = script[:-4]
                self.cursor.execute(script, list(conditions.values()))
            else:
                self.cursor.execute(script)
        else:
            self.cursor.execute(script)
        result = self.cursor.fetchall()

        return result

    def insert(self, table_name, row: dict):
        """

        :param table_name:
        :param row: Can be [{field_A:value,...},...] or {field_A:value,...}
        :param pattern:
        :return:
        """
        # Prepare data
        column_names = ", ".join(row.keys())
        column_values = tuple(x for x in row.values())
        # Generate the SQL query
        script = r"""INSERT INTO {} ({}) VALUES {}""".format(table_name, column_names, column_values)

        if self.db is None:
            self.connect()

        try:
            self.cursor.execute(script)
        except Exception as e:
            warnings.warn("Error mes:{} \nScript: {}".format(e, script), Warning)
            return
        self.db.commit()

    def delete(self, table_name, conditions: dict):
        # Generate the DELETE statement
        script = "DELETE FROM {} WHERE".format(table_name)

        if self.db is None:
            self.connect()

        # Add the WHERE clause using the dictionary values
        for key, value in conditions.items():
            script += " {} = %s AND".format(key)
        # Remove the last 'AND' from the WHERE clause
        script = script[:-4]
        self.cursor.execute(script, list(conditions.values()))

    def update(self, table_name, conditions: dict, new_cols: dict):
        if self.db is None:
            self.connect()

        # Generate a list of column=value pairs for the SET clause
        set_pairs = [f"{column}=%s" for column, value in new_cols.items()]

        # Generate a list of column=value pairs for the WHERE clause
        where_pairs = [f"{column}=%s" for column, value in conditions.items()]

        # Join the column=value pairs with commas and combine them into the final SQL query
        set_clause = ", ".join(set_pairs)
        where_clause = " AND ".join(where_pairs)
        all_values = list(new_cols.values()) + list(conditions.values())
        script = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        self.cursor.execute(script, all_values)
        self.db.commit()


def create_table():
    """
    Create table method and class if they do not exist.
    """
    db = database()
    sql_script = """
        CREATE TABLE IF NOT EXISTS `class` (
        `id` INT AUTO_INCREMENT PRIMARY KEY,
        `project_name` VARCHAR(255) NOT NULL,
        `class_name` VARCHAR(255) NOT NULL,
        `class_path` VARCHAR(255) NOT NULL,
        `signature` TEXT NOT NULL,
        `super_class` TEXT NULL,
        `package` TEXT NULL,
        `imports` TEXT NULL,
        `fields` LONGTEXT NULL,
        `has_constructor` TINYINT(1) NOT NULL,
        `dependencies` TEXT NULL,
        CONSTRAINT `project_name` UNIQUE (`project_name`, `class_name`)
    );
        CREATE TABLE IF NOT EXISTS `method` (
        `id` INT AUTO_INCREMENT PRIMARY KEY,
        `project_name` VARCHAR(255) NOT NULL,
        `signature` TEXT NOT NULL,
        `method_name` VARCHAR(255) NOT NULL,
        `parameters` TEXT NOT NULL,
        `source_code` LONGTEXT NOT NULL,
        `class_name` VARCHAR(255) NOT NULL,
        `dependencies` LONGTEXT NULL,
        `use_field` TINYINT(1) NOT NULL,
        `is_constructor` TINYINT(1) NOT NULL,
        `is_get_set` TINYINT(1) NOT NULL,
        `is_public` TINYINT(1) NOT NULL
    );
    """
    db.execute(sql_script)


def drop_table():
    """
    Truncate table method and class if they do exist.
    """
    db = database()
    sql_script = """
        DROP TABLE `class`;
        DROP TABLE `method`;
    """
    db.execute(sql_script)
