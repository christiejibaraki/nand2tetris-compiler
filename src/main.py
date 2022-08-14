"""
Main module
Runs first part of compiler, the Jack "Analyzer"
"""
import sys
import os
from io_utility import read_file, clean_code, write_file
from compilation_engine import CompilationEngine


def compile_jack_program(input_file_path):
    """
    Compile a jack program

    :param input_file_path: (str) path to input file
    :return: (str) vm code
    """
    orig_input_str = read_file(input_file_path)
    clean_input_str = clean_code(orig_input_str)
    compilation_engine = CompilationEngine(clean_input_str)
    print("class table\n", compilation_engine.get_symbol_table().get_class_table())
    print("last subroutine table\n", compilation_engine.get_symbol_table().get_subroutine_table())
    return compilation_engine.get_output()


if __name__ == "__main__":
    dir_input = sys.argv[1]
    path = os.path.realpath(dir_input)
    directory_name = os.path.basename(path)
    # traverse files in dir
    # if .jack extension, translate file
    for filename in os.listdir(path):
        name, extension = os.path.splitext(filename)
        if extension == ".jack":
            print(f"*** Compiling {filename}")
            output = compile_jack_program(os.path.join(path, filename))
            out_filename = name + ".vm"
            out_file_path = os.path.join(path, out_filename)
            write_file(out_file_path, output)
            print(f"--- Writing output file {out_filename} to {path}")
