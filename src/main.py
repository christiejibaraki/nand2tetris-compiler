"""
Main module
Runs first part of compiler
Translates .jack files
"""
import sys
import os
from utility import read_file, clean_code, write_file
from tokenizer import Tokenizer


def translate_file(input_file_path):
    """
    Tokenize and tag jack program

    :param input_file_path: (str) path to input file
    :return: (str) xml representing syntactic structure of program
    """
    orig_input_str = read_file(input_file_path)
    clean_input_sr = clean_code(orig_input_str)
    tokenizer = Tokenizer(clean_input_sr)
    return tokenizer.get_xml()


if __name__ == "__main__":
    dir_input = sys.argv[1]
    path = os.path.realpath(dir_input)
    directory_name = os.path.basename(path)
    # traverse files in dir
    # if .jack extension, translate file
    for filename in os.listdir(path):
        name, extension = os.path.splitext(filename)
        if extension == ".jack":
            print(f"*** Translating {filename}")
            output = translate_file(os.path.join(path, filename))
            out_filename = name + "_T.xml"
            out_file_path = os.path.join(path, out_filename)
            print(output)
            write_file(out_file_path, output)
            print(f"*** Writing output file {out_filename} to {path}")
