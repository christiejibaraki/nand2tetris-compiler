"""
VM Writer Module
Output module for generating VM code
"""
from grammar_utility import \
    STRING_CONSTANT_TAG, INTEGER_CONSTANT_TAG, KEYWORD_CONSTANT

TOKEN_TO_VM_ARITHMETIC = {
    "+": "add",
    "-": "sub",
    "&": "and", "&amp;": "and",
    "|": "or",
    "<": "lt", "&lt;": "lt",
    ">": "gt", "&gt;": "gt",
    "=": "eq"
}

ARGUMENT_SEGMENT = "argument"
CONSTANT_SEGMENT = "constant"
POINTER_SEGMENT = "pointer"
TEMP_SEGMENT = "temp"
THAT_SEGMENT = "that"

SYMBOL_TABLE_TO_VM_SEGMENT = {
    "static": "static",
    "field": "this",
    "arg": ARGUMENT_SEGMENT, ARGUMENT_SEGMENT: ARGUMENT_SEGMENT,
    "var": "local", "local": "local",
    POINTER_SEGMENT: POINTER_SEGMENT,
    CONSTANT_SEGMENT: CONSTANT_SEGMENT,
    TEMP_SEGMENT: TEMP_SEGMENT,
    THAT_SEGMENT: THAT_SEGMENT
}


class VMWriter:
    """
    Outputs VM commands
    """

    def __init__(self):
        self.__output = ""

    def get_output(self):
        """
        Get VM commands
        :return: (str) VM commands
        """
        return self.__output

    """
    Expressions, terms
    """
    def write_op(self, operator):
        """
        Write VM command for an operator in an expression
        operators are:
        '+', '-', '*', '/', '&', '|', '<', '>', '=', "&lt;", "&gt;", "&amp;"
        :param operator: (str) an operator
        :return: NA, update self.output
        """
        if operator == "*":
            self.write_call_command("Math.multiply", 2)
        elif operator == "/":
            self.write_call_command("Math.divide", 2)
        else:
            if not operator in TOKEN_TO_VM_ARITHMETIC:
                raise KeyError(f"Expected operator token, actual: {operator}")
            self.write_arithmetic_command(TOKEN_TO_VM_ARITHMETIC[operator])

    def write_constant_int_string_keyword(self, token_type, token):
        """
        Write VM command for term token that is:
            integer constant, string constant, or keyword constant
        :param token: (str) represents a term in an expression
        :return: NA, update self.output
        """

        # integer constant
        if token_type == INTEGER_CONSTANT_TAG:
            self.write_push_command(CONSTANT_SEGMENT, token)
        # string constant
        elif token_type == STRING_CONSTANT_TAG:
            self.write_comment(f"string constant: {token}")
            string_length = len(token)
            self.write_push_command(CONSTANT_SEGMENT, string_length)
            self.write_call_command("String.new", 1)
            for i in range(string_length):
                self.write_push_command(CONSTANT_SEGMENT, ord(token[i]))
                self.write_call_command("String.appendChar", 2)
        # keyword constant
        elif token in KEYWORD_CONSTANT:
            if token == "this":
                self.write_push_command(POINTER_SEGMENT, 0)
            elif token == "true":
                self.write_push_command(CONSTANT_SEGMENT, 1)
                self.write_arithmetic_command("neg")
            elif token in ("null", "false"):
                self.write_push_command(CONSTANT_SEGMENT, 0)
            else:
                raise ValueError(f"Invalid keyword {token}")
        else:
            raise ValueError("Invalid term. "
                             "Expecting integer, string or keyword constant. "
                             f"Actual: {token_type}, {token}")

    def write_unary_op(self, operator):
        """
        Write VM command for a unary operate ~ or -
        :param operator: (str) unary operator
        :return: NA, update self.output
        """
        if operator == "-":
            self.write_arithmetic_command("neg")
        elif operator == "~":
            self.write_arithmetic_command("not")
        else:
            raise ValueError(f"Expecting unary operator, actual {operator}")

    """
    Basic Commands
    """
    def write_push_command(self, segment, index):
        """
        Write push command
        :param segment: (str) memory segment
        :param index: (int) index
        :return: NA
        """
        segment = SYMBOL_TABLE_TO_VM_SEGMENT[segment]
        self.__output += f"push {segment} {str(index)}\n"

    def write_pop_command(self, segment, index):
        """
        Write pop command
        :param segment: (str) memory segment
        :param index: (int) index
        :return: NA
        """
        segment = SYMBOL_TABLE_TO_VM_SEGMENT[segment]
        self.__output += f"pop {segment} {str(index)}\n"

    def write_arithmetic_command(self, command):
        """
        Write arithmetic command
        :param command: (str) the command
        :return: NA
        """
        self.__output += f"{command}\n"

    def write_label_command(self, label):
        """
        Write label command
        :param label: (str) the label
        :return: NA
        """
        self.__output += f"label {label}\n"

    def write_goto_command(self, label):
        """
        Write goto command
        :param label: (str) label to goto
        :return: NA
        """
        self.__output += f"goto {label}\n"

    def write_if_command(self, label):
        """
        Write if-goto command
        :param label: (str) label to goto
        :return: NA
        """
        self.__output += f"if-goto {label}\n"

    def write_call_command(self, name, nArgs):
        """
        Write command to call a function
        :param name: (str) name of the function
        :param nArgs: (int) number of arguments the function takes
        :return: NA
        """
        self.__output += f"call {name} {str(nArgs)}\n"

    def write_function_command(self, name, nLocals):
        """
        Write command to declare a function
        :param name: (str) name of the function
        :param nLocals: (int) number of local variables
        :return: NA
        """
        self.__output += f"function {name} {str(nLocals)}\n"

    def write_void_return(self):
        """
        Write vm commands for subroutine with return type void
        :return: NA
        """
        self.write_push_command(CONSTANT_SEGMENT, 0)
        self.write_return_command()

    def write_return_command(self):
        """
        Write return command
        :return: NA
        """
        self.__output += "return\n"

    def write_comment(self, comment_text):
        """
        Write a comment
        :param comment_text: (str) text of the comment
        :return: NA
        """
        self.__output += f"// {comment_text}\n"
