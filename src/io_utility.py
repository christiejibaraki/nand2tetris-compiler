"""
Utility functions
"""
import re

REGEX_MULTI_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
REGEX_SINGLE_COMMENT = re.compile(r"//.*?\n")
REGEX_WHITESPACE = re.compile(r"[^\S\r\n]")
REGEX_MULTI_NEWLINE = re.compile(r"\n+")


def read_file(file_path):
    """
    Read file to string
    :param file_path: file path
    :return: string
    """
    with open(file_path) as f:
        lines = f.readlines()
        return ''.join(lines)


def write_file(file_path, string):
    """
    Write a string to a file
    :param file_path: file path
    :param string: string to write
    :return: NA, writes file
    """
    with open(file_path, 'w') as f:
        f.write(string)


def clean_code(string):
    """
    Strip whitespace (spaces, tabs, blank lines)
    And removes comments
    :param string: string
    :return: clean line if not empty. otherwise returns None
    """
    clean_string = re.sub(REGEX_MULTI_COMMENT, "", string)
    clean_string = re.sub(REGEX_SINGLE_COMMENT, "\n", clean_string + "\n")
    # clean_string = re.sub(REGEX_WHITESPACE, "", clean_string)
    clean_string = re.sub(REGEX_MULTI_NEWLINE, "\n", clean_string)
    return clean_string.strip()