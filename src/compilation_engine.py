"""
Compilation Engine Module
"""
from tokenizer import Tokenizer
from grammar_utility import \
    KEYWORD_TAG, IDENTIFIER_TAG, SYMBOL_TAG, STRING_CONSTANT_TAG, INTEGER_CONSTANT_TAG, \
    SYMBOLS, KEYWORDS
from grammar_utility import SUBROUTINE_OR_CLASS_END, SUBROUTINE_DEC_SET


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

    def _validate_token(self, source, target, error_message_input, offset):
        """
        Validates current token
            If valid:
                return xml tag and advance tokenizer
            Otherwise raise error
        :param source: (str) token or type to compare
        :param target: {str} set of expected values
        :param error_message_input: (str) description of target values
        :param offset: (str) tab offset
        :return: (str) xml output for current token
        """

        if source in target:
            out = offset + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()
            return out

        error_message = f"Expecting {error_message_input}, actual: " \
                        f"{self.tokenizer.current_type()}: " \
                        f"{self.tokenizer.current_token()}"

        raise ValueError(error_message)

    def compile_class(self):
        """
        Compiles a complete class
        :return: (str) xml output
        """
        output_str = "<class>\n"
        current_offset = "\t"
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {"class"}, "keyword class", current_offset)

        # expect className identifier
        output_str += self._validate_token(self.tokenizer.current_type(),
                                           {IDENTIFIER_TAG}, "identifier", current_offset)

        # expect {
        output_str += self._validate_token(self.tokenizer.current_token(),
                                          {"{"}, "{", current_offset)

        # optional class variable declarations
        while not (self.tokenizer.current_token() in SUBROUTINE_OR_CLASS_END):
            if self.tokenizer.current_token() in {"static", "field"}:
                output_str += self.compile_class_var_dec(current_offset)

        # optional subroutines
        #while self.tokenizer.current_token() != "}":
        if self.tokenizer.current_token() in SUBROUTINE_DEC_SET:
            output_str += self.compile_subroutine(current_offset)

        # expect "}"
        return output_str

    def compile_class_var_dec(self, current_offset):
        """
        Compiles a static declaration or a field declaration
        :param current_offset: (str) tab for parent tag
        :return: (str) xml for class var dec
        """
        output_str = current_offset + "<classVarDec>" + "\n"
        new_offset = current_offset + "\t"

        # guaranteed to be static or field
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        # expect a variable type (either a keyword or identifier)
        output_str += self._validate_token(self.tokenizer.current_type(),
                                           {KEYWORD_TAG, IDENTIFIER_TAG},
                                           "keyword or identifier",
                                           new_offset)

        # expect at least one variable name
        output_str += self._validate_token(self.tokenizer.current_type(),
                                           {IDENTIFIER_TAG}, "variable name",
                                           new_offset)

        # parse additional variable names
        while self.tokenizer.current_token() != ";":
            if self.tokenizer.current_token() == ",":
                output_str += self._validate_token(self.tokenizer.current_token(),
                                                   {","}, ",",
                                                   new_offset)
                continue
            if self.tokenizer.current_type() == IDENTIFIER_TAG:
                output_str += self._validate_token(self.tokenizer.current_type(),
                                                   {IDENTIFIER_TAG}, "variable name",
                                                   new_offset)
            else:
                raise ValueError("Expecting variable name")

        # expected ;
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {";"},
                                           ";",
                                           new_offset)

        output_str += current_offset + "</classVarDec>" + "\n"
        return output_str

    def compile_subroutine(self, current_offset):
        """
        Compiles a complete method, function, or constructor
        :param current_offset: (str) tab for parent tag
        :return: (str) xml for class var dec
        """
        output_str = current_offset + "<subroutineDec>" + "\n"
        dec_offset = current_offset + "\t"

        # guaranteed to be constructor, function, or method
        output_str += dec_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        # expect void or type (int, char, boolean, classname)
        output_str += self._validate_token(self.tokenizer.current_type(),
                                           {KEYWORD_TAG, IDENTIFIER_TAG},
                                           "keyword or identifier",
                                           dec_offset)

        # expect a subroutine name
        output_str += self._validate_token(self.tokenizer.current_type(),
                                           {IDENTIFIER_TAG}, "subroutine name",
                                           dec_offset)

        # expect (
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {"("}, "(", dec_offset)

        # parameter list
        output_str += self.compile_paramater_list(dec_offset)

        # expect )
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {")"}, ")",  dec_offset)
        # expect {
        # subroutineBody
        # expect }

        output_str += current_offset + "</subroutineDec" + "\n"
        return output_str

    def compile_paramater_list(self, current_offset):
        """
        Compiles a (possibly empty) parameter list
        :param current_offset: (str) tab for parent tag
        :return:
        """
        output_str = current_offset + "<parameterList>" + "\n"
        var_offset = current_offset + "\t"

        while self.tokenizer.current_token() != ")":
            if self.tokenizer.current_token() == ",":
                output_str += self._validate_token(self.tokenizer.current_token(),
                                                   {","}, ",",
                                                   var_offset)
                continue
            output_str += self._validate_token(self.tokenizer.current_type(),
                                               {KEYWORD_TAG, IDENTIFIER_TAG},
                                               "var type",
                                               var_offset)
            output_str += self._validate_token(self.tokenizer.current_type(),
                                               {IDENTIFIER_TAG},
                                               "var name",
                                               var_offset)

        output_str += current_offset + "</parameterList>" + "\n"
        return output_str
