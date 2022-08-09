"""
Compilation Engine Module
"""
from tokenizer import Tokenizer
from grammar_utility import \
    KEYWORD_TAG, IDENTIFIER_TAG, SYMBOL_TAG, STRING_CONSTANT_TAG, INTEGER_CONSTANT_TAG, \
    SYMBOLS, KEYWORDS
from grammar_utility import SUBROUTINE_DEC_SET


class CompilationEngine:
    """
    Effects the actual compilation output.
        Gets its input from a JackTokenizer and
        emits its parsed structure into an output string
    """
    def __init__(self, input_str):
        """
        :param input_str: (str) jack code (comments removed)
        """
        self.tokenizer = Tokenizer(input_str)
        self.tokenizer.next()
        if not self.tokenizer.current_token() == "class":
            error_message = "Syntax Error: Expecting keyword \"class\", " \
                            f"actual token: {self.tokenizer.current_token()}"
            raise ValueError(error_message)

        self.__output = self.compile_class()

    def get_output(self):
        """
        Returns the output constructed by the compilation engine
        :return: (str) xml representing parse tree
        """
        return self.__output

    def compile_class(self):
        output_str = "<class>\n"
        output_str += "\t" + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        # expect className identifier
        if self.tokenizer.current_type() == IDENTIFIER_TAG:
            output_str += "\t" + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()
        else:
            error_message = f"Expecting identifier, actual: " \
                            f"{self.tokenizer.current_type()}: " \
                            f"{self.tokenizer.current_token()}"
            raise ValueError(error_message)

        # expect {
        if self.tokenizer.current_token() == "{":
            output_str += "\t" + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()
        else:
            raise ValueError("Expecting { after classname")

        # expect optional class variable declarations followed by optional subroutine declarations
        while not (self.tokenizer.current_token() in SUBROUTINE_DEC_SET or
                   SUBROUTINE_DEC_SET == "}"):
            if self.tokenizer.current_token() in {"static", "field"}:
                output_str += self.compile_class_var_dec()
                self.tokenizer.next()

        if self.tokenizer.current_token() in SUBROUTINE_DEC_SET:
            output_str += "\t" + self.compile_subroutine()
            self.tokenizer.next()

        # if self.tokenizer.get_current_token() == "}":
        #     output_str += "\t" + self.tokenizer.get_current_tag() + "\n"
        return output_str

    def compile_class_var_dec(self):
        output_str = "\t" + "<classVarDec>" + "\n"
        output_str += "\t\t" + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        # expect a variable type (either a keyword or identifier)
        if self.tokenizer.current_type() in {KEYWORD_TAG, IDENTIFIER_TAG}:
            output_str += "\t\t" + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()
        else:
            error_message = f"Expecting keyword or identifier, actual: " \
                            f"{self.tokenizer.current_type()}: " \
                            f"{self.tokenizer.current_token()}"
            raise ValueError(error_message)

        # expect at least one variable name
        if self.tokenizer.current_type() == IDENTIFIER_TAG:
            output_str += "\t\t" + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()
        else:
            raise ValueError("Expecting variable name")

        while self.tokenizer.current_token()!= ";":
            if self.tokenizer.current_token() == ",":
                output_str += "\t\t" + self.tokenizer.current_tag() + "\n"
                self.tokenizer.next()
                continue
            if self.tokenizer.current_type() == IDENTIFIER_TAG:
                output_str += "\t\t" + self.tokenizer.current_tag() + "\n"
                self.tokenizer.next()
            else:
                raise ValueError("Expecting variable name")

        output_str += "\t\t" + self.tokenizer.current_tag() + "\n"
        output_str += "\t" + "</classVarDec>" + "\n"
        return output_str

    def compile_subroutine(self):
        return ""

