"""
Compilation Engine Module
"""
from tokenizer import Tokenizer
from grammar_utility import \
    KEYWORD_TAG, IDENTIFIER_TAG, SYMBOL_TAG, STRING_CONSTANT_TAG, INTEGER_CONSTANT_TAG, \
    SYMBOLS, KEYWORDS
from grammar_utility import SUBROUTINE_OR_CLASS_END, SUBROUTINE_DEC_SET, \
    STATEMENT_OR_ROUTINE_END


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

    """
    Program structure methods
    """
    def compile_class(self):
        """
        Compiles a complete class
        :return: (str) xml output
        """
        current_tag = "class"
        output_str = f"<{current_tag}>\n"
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
        while self.tokenizer.current_token() != "}":
            if self.tokenizer.current_token() in SUBROUTINE_DEC_SET:
                output_str += self.compile_subroutine(current_offset)

        # expect "}"
        temp = "}"
        if self.tokenizer.current_token() != "}":
            raise ValueError(f"Expecting {temp}, actual {self.tokenizer.current_token()}")

        output_str += current_offset + self.tokenizer.current_tag() + "\n"
        output_str += f"</{current_tag}>" + "\n"
        return output_str

    def compile_class_var_dec(self, current_offset):
        """
        Compiles a static declaration or a field declaration
        :param current_offset: (str) tab for parent tag
        :return: (str) xml for class var dec
        """
        current_tag = "classVarDec"
        output_str = current_offset + f"<{current_tag}>" + "\n"
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

        # guaranteed to be ;
        output_str += new_offset+ self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def compile_subroutine(self, current_offset):
        """
        Compiles a complete method, function, or constructor
        :param current_offset: (str) tab for parent tag
        :return: (str) xml for class var dec
        """
        current_tag = "subroutineDec"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + "\t"

        # guaranteed to be constructor, function, or method
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        # expect void or type (int, char, boolean, classname)
        output_str += self._validate_token(self.tokenizer.current_type(),
                                           {KEYWORD_TAG, IDENTIFIER_TAG},
                                           "keyword or identifier",
                                           new_offset)

        # expect a subroutine name
        output_str += self._validate_token(self.tokenizer.current_type(),
                                           {IDENTIFIER_TAG}, "subroutine name",
                                           new_offset)

        # expect (
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {"("}, "(", new_offset)

        # parameter list
        output_str += self.compile_paramater_list(new_offset)

        # expect )
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {")"}, ")",  new_offset)
        # expect {
        # subroutineBody
        if self.tokenizer.current_token() == "{":
            output_str += self.compile_subroutine_body(new_offset)
        else:
            raise ValueError("Expecting start of subroutine body {")

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def compile_paramater_list(self, current_offset):
        """
        Compiles a (possibly empty) parameter list
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "parameterList"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + "\t"

        while self.tokenizer.current_token() != ")":
            if self.tokenizer.current_token() == ",":
                output_str += self._validate_token(self.tokenizer.current_token(),
                                                   {","}, ",",
                                                   new_offset)
                continue
            output_str += self._validate_token(self.tokenizer.current_type(),
                                               {KEYWORD_TAG, IDENTIFIER_TAG},
                                               "var type",
                                               new_offset)
            output_str += self._validate_token(self.tokenizer.current_type(),
                                               {IDENTIFIER_TAG},
                                               "var name",
                                               new_offset)

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def compile_subroutine_body(self, current_offset):
        """
        Compiles a (possibly empty) parameter list
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "subroutineBody"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + "\t"

        # guaranteed to be "{"
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        # compile any variable declarations
        while self.tokenizer.current_token() not in STATEMENT_OR_ROUTINE_END:
            output_str += self.compile_var_dec(new_offset)

        # compile any statements
        while self.tokenizer.current_token() != "}":
            output_str += self.compile_statements(current_offset)

        # guaranteed to be "}"
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def compile_var_dec(self, current_offset):
        """
        Compiles a var declaration
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "varDec"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + "\t"

        # guaranteed to be var
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        #TODO this code is duplicated from compile_class_var_dec
        # expect a variable type (either a keyword or identifier)
        output_str += self._validate_token(self.tokenizer.current_type(),
                                           {KEYWORD_TAG, IDENTIFIER_TAG},
                                           "keyword or identifier",
                                           new_offset)

        # expect at least one variable name
        output_str += self._validate_token(self.tokenizer.current_type(),
                                           {IDENTIFIER_TAG}, "variable name",
                                           new_offset)

        # optional additional variable names
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
                raise ValueError(f"Expecting variable name, actual: {self.tokenizer.current_token()}")

        # guaranteed to be ;
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    """
    Statement methods
    """
    def compile_statements(self, current_offset):
        """
        Compiles a sequence of statements, not including the enclosing “{}”.
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "statements"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + "\t"

        while self.tokenizer.current_token() != "}":
            current_token = self.tokenizer.current_token()
            if current_token == "do":
                output_str += self.compile_do_statement(new_offset)
                continue
            if current_token == "let":
                output_str += self.compile_let_statement(new_offset)
                continue
            if current_token == "while":
                output_str += self.compile_while_statement(new_offset)
                continue
            if current_token == "return":
                output_str += self.compile_return_statement(new_offset)
                continue
            if current_token == "if":
                output_str += self.compile_if_statement(new_offset)
                continue
            raise ValueError("Expecting do, let, while, return, or if")

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def compile_do_statement(self, current_offset):
        """
        Compiles a do statement
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "doStatement"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + "\t"

        # guaranteed to be do
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        # expect a subroutine name OR (class or variable name)
        output_str += self._validate_token(self.tokenizer.current_type(),
                                           {IDENTIFIER_TAG}, "identifier",
                                           new_offset)

        # if previous token was a class or variable name
        # next tokens should be "." and a subroutine name
        if self.tokenizer.current_token() == ".":
            output_str += new_offset + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()
            output_str += self._validate_token(self.tokenizer.current_type(),
                                               {IDENTIFIER_TAG}, "identifier",
                                               new_offset)

        # expect "(", followed by an expression list, and ")"
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {"("}, "(", new_offset)
        output_str += self.compile_expression_list(new_offset)

        # guaranteed to be )
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        # expect ;
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {";"}, ";", new_offset)

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def compile_let_statement(self, current_offset):
        """
        Compiles a let statement
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "letStatement"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + "\t"

        # guaranteed to be let
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        # expecting varname
        output_str += self._validate_token(self.tokenizer.current_type(),
                                           {IDENTIFIER_TAG}, "identifier",
                                           new_offset)

        # optional [expression]
        if self.tokenizer.current_token() == "[":
            output_str += new_offset + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()
            output_str += self.compile_expression()
            output_str += self._validate_token(self.tokenizer.current_token(),
                                               {"]"}, "]",
                                               new_offset)
        # expect "="
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {"="}, "=",
                                           new_offset)
        # expect expression
        output_str += self.compile_expression(new_offset)

        # expect ;
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {";"}, ";", new_offset)

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def compile_while_statement(self, current_offset):
        """
        Compiles a while statement
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "whileStatement"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + "\t"

        # guaranteed to be while
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        # expect (
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {"("}, ")", new_offset)

        output_str += self.compile_expression(new_offset)

        # expect )
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {")"}, ")", new_offset)

        # expect {
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {"{"}, "{", new_offset)
        # optional statements
        output_str += self.compile_statements(new_offset)

        # guaranteed to be }
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def compile_return_statement(self, current_offset):
        """
        Compiles a return statement
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "returnStatement"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + "\t"

        # guaranteed to be return
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        if self.tokenizer.current_token() != ";":
            output_str += self.compile_expression(new_offset)

        # expect ;
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {";"}, ";", new_offset)

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def compile_if_statement(self, current_offset):
        """
        Compiles an if statement
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "ifStatement"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + "\t"

        # guaranteed to be if
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        # expect (
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {"("}, ")", new_offset)

        output_str += self.compile_expression(new_offset)

        # expect )
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {")"}, ")", new_offset)

        # expect {
        output_str += self._validate_token(self.tokenizer.current_token(),
                                           {"{"}, "{", new_offset)
        # optional statements
        output_str += self.compile_statements(new_offset)

        # guaranteed to be }
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        # optional else
        if self.tokenizer.current_token() == "else":
            output_str += new_offset + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()

            # expect {
            output_str += self._validate_token(self.tokenizer.current_token(),
                                               {"{"}, "{", new_offset)
            # optional statements
            output_str += self.compile_statements(new_offset)

            # guaranteed to be }
            output_str += new_offset + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    """
    Expression methods
    """
    def compile_expression_list(self, current_offset):
        """
        Compiles a (possibly empty) commaseparated list of expressions.
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "expressionList"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + "\t"

        while self.tokenizer.current_token() != ")":
            if self.tokenizer.current_token() == ",":
                output_str += self._validate_token(self.tokenizer.current_token(),
                                                   {","}, ",",
                                                   new_offset)
                continue
            output_str += self.compile_expression(new_offset)

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def compile_expression(self, current_offset):
        """
        Compiles an expression.
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "expression"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + "\t"

        output_str += self.compile_term(new_offset)

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def compile_term(self, current_offset):
        """
        Compiles a term.

        If the current token is an identifer,
            may be a variable, array entry, or subroutine call

        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "term"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + "\t"

        # TODO update
        # for expression less square dance
        output_str += self._validate_token(self.tokenizer.current_type(),
                                           {IDENTIFIER_TAG, KEYWORD_TAG}, "identifier or keyword",
                                           new_offset)

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str