"""
Compilation Engine Module
"""
from tokenizer import Tokenizer
from grammar_utility import \
    KEYWORD_TAG, IDENTIFIER_TAG, STRING_CONSTANT_TAG, INTEGER_CONSTANT_TAG
from grammar_utility import SUBROUTINE_OR_CLASS_END, SUBROUTINE_DEC_SET, \
    STATEMENT_OR_ROUTINE_END, TERM_OPS, KEYWORD_CONSTANT, UNARY_OP

OFFSET_CHAR = "  "


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

        self.__output = self._compile_class()

    def get_output(self):
        """
        Returns the output constructed by the compilation engine
        :return: (str) xml representing parse tree
        """
        return self.__output

    """
    Program structure methods
    """
    def _compile_class(self):
        """
        Compiles a complete class
        :return: (str) xml output
        """
        current_tag = "class"
        output_str = f"<{current_tag}>\n"
        current_offset = OFFSET_CHAR
        output_str += self._validate_token_and_advance(
            {"class"}, "keyword class", current_offset)

        # expect className identifier
        output_str += self._validate_type_and_advance(
            {IDENTIFIER_TAG}, "identifier", current_offset)

        # expect {
        output_str += self._validate_token_and_advance({"{"}, "{", current_offset)

        # optional class variable declarations
        while not self.tokenizer.current_token() in SUBROUTINE_OR_CLASS_END:
            if self.tokenizer.current_token() in {"static", "field"}:
                output_str += self._compile_class_var_dec(current_offset)

        # optional subroutines
        while self.tokenizer.current_token() != "}":
            if self.tokenizer.current_token() in SUBROUTINE_DEC_SET:
                output_str += self._compile_subroutine(current_offset)

        # expect "}"
        temp = "}"
        if self.tokenizer.current_token() != "}":
            raise ValueError(f"Expecting {temp}, actual {self.tokenizer.current_token()}")

        output_str += current_offset + self.tokenizer.current_tag() + "\n"
        output_str += f"</{current_tag}>" + "\n"
        return output_str

    def _compile_class_var_dec(self, current_offset):
        """
        Compiles a static declaration or a field declaration
        :param current_offset: (str) tab for parent tag
        :return: (str) xml for class var dec
        """
        current_tag = "classVarDec"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        # guaranteed to be static or field
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()
        # type varName (,varName)*
        output_str += self._compile_var_list(new_offset)

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def _compile_subroutine(self, current_offset):
        """
        Compiles a complete method, function, or constructor
        :param current_offset: (str) tab for parent tag
        :return: (str) xml for class var dec
        """
        current_tag = "subroutineDec"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        # guaranteed to be constructor, function, or method
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        # expect void or type (int, char, boolean, classname)
        output_str += self._validate_type_and_advance({KEYWORD_TAG, IDENTIFIER_TAG},
                                                      "keyword or identifier", new_offset)

        # expect a subroutine name
        output_str += self._validate_type_and_advance({IDENTIFIER_TAG}, "subroutine name",
                                                      new_offset)
        # expect (
        output_str += self._validate_token_and_advance({"("}, "(", new_offset)
        # parameter list
        output_str += self._compile_paramater_list(new_offset)
        # expect )
        output_str += self._validate_token_and_advance({")"}, ")", new_offset)

        # expect {
        # subroutineBody
        if self.tokenizer.current_token() == "{":
            output_str += self._compile_subroutine_body(new_offset)
        else:
            raise ValueError("Expecting start of subroutine body {")

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def _compile_paramater_list(self, current_offset):
        """
        Compiles a (possibly empty) parameter list
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "parameterList"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        while self.tokenizer.current_token() != ")":
            if self.tokenizer.current_token() == ",":
                output_str += self._validate_token_and_advance({","}, ",", new_offset)
                continue
            output_str += self._validate_type_and_advance({KEYWORD_TAG, IDENTIFIER_TAG},
                                                          "var type", new_offset)
            output_str += self._validate_type_and_advance({IDENTIFIER_TAG},
                                                          "var name", new_offset)

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def _compile_subroutine_body(self, current_offset):
        """
        Compiles a (possibly empty) parameter list
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "subroutineBody"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        # guaranteed to be "{"
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        # compile any variable declarations
        while self.tokenizer.current_token() not in STATEMENT_OR_ROUTINE_END:
            output_str += self._compile_var_dec(new_offset)

        # compile any statements
        while self.tokenizer.current_token() != "}":
            output_str += self._compile_statements(new_offset)

        # guaranteed to be "}"
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def _compile_var_dec(self, current_offset):
        """
        Compiles a var declaration
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "varDec"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        # guaranteed to be var
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()
        # type varName (,varName)*
        output_str += self._compile_var_list(new_offset)

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    """
    Statement methods
    """
    def _compile_statements(self, current_offset):
        """
        Compiles a sequence of statements, not including the enclosing “{}”.
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "statements"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        while self.tokenizer.current_token() != "}":
            current_token = self.tokenizer.current_token()
            if current_token == "do":
                output_str += self._compile_do_statement(new_offset)
                continue
            if current_token == "let":
                output_str += self._compile_let_statement(new_offset)
                continue
            if current_token == "while":
                output_str += self._compile_while_statement(new_offset)
                continue
            if current_token == "return":
                output_str += self._compile_return_statement(new_offset)
                continue
            if current_token == "if":
                output_str += self._compile_if_statement(new_offset)
                continue
            raise ValueError("Expecting do, let, while, return, or if")

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def _compile_do_statement(self, current_offset):
        """
        Compiles a do statement
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "doStatement"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        # guaranteed to be do
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()
        # subroutine call
        output_str += self._compile_subroutine_call(new_offset)
        # expect ;
        output_str += self._validate_token_and_advance({";"}, ";", new_offset)

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def _compile_let_statement(self, current_offset):
        """
        Compiles a let statement
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "letStatement"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        # guaranteed to be let
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()
        # expecting varname
        output_str += self._validate_type_and_advance({IDENTIFIER_TAG}, "identifier",
                                                      new_offset)
        # optional [expression]
        if self.tokenizer.current_token() == "[":
            output_str += new_offset + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()
            output_str += self._compile_expression(new_offset, {"]"})
            output_str += self._validate_token_and_advance({"]"}, "]", new_offset)
        # expect "="
        output_str += self._validate_token_and_advance({"="}, "=", new_offset)
        # expect expression
        output_str += self._compile_expression(new_offset, {";"})
        # expect ;
        output_str += self._validate_token_and_advance({";"}, ";", new_offset)

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def _compile_while_statement(self, current_offset):
        """
        Compiles a while statement
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "whileStatement"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        # guaranteed to be while
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()
        # expect (
        output_str += self._validate_token_and_advance({"("}, ")", new_offset)
        # expression
        output_str += self._compile_expression(new_offset, {")"})
        # expect )
        output_str += self._validate_token_and_advance({")"}, ")", new_offset)
        # expect {
        output_str += self._validate_token_and_advance({"{"}, "{", new_offset)
        # optional statements
        output_str += self._compile_statements(new_offset)
        # guaranteed to be }
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def _compile_return_statement(self, current_offset):
        """
        Compiles a return statement
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "returnStatement"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        # guaranteed to be return
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()
        # if not empty return, expression
        if self.tokenizer.current_token() != ";":
            output_str += self._compile_expression(new_offset, {";"})
        # expect ;
        output_str += self._validate_token_and_advance({";"}, ";", new_offset)

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def _compile_if_statement(self, current_offset):
        """
        Compiles an if statement
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "ifStatement"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        # guaranteed to be if
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()
        # expect (
        output_str += self._validate_token_and_advance({"("}, ")", new_offset)
        # expression
        output_str += self._compile_expression(new_offset, {")"})
        # expect )
        output_str += self._validate_token_and_advance({")"}, ")", new_offset)
        # expect {
        output_str += self._validate_token_and_advance({"{"}, "{", new_offset)
        # optional statements
        output_str += self._compile_statements(new_offset)
        # guaranteed to be }
        output_str += new_offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        # optional else block
        if self.tokenizer.current_token() == "else":
            output_str += new_offset + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()
            # expect {
            output_str += self._validate_token_and_advance({"{"}, "{", new_offset)
            # optional statements
            output_str += self._compile_statements(new_offset)
            # guaranteed to be }
            output_str += new_offset + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    """
    Expression methods
    """
    def _compile_expression_list(self, current_offset):
        """
        Compiles a (possibly empty) commaseparated list of expressions.
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "expressionList"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        # compile expressions until hit ")"
        while self.tokenizer.current_token() != ")":
            if self.tokenizer.current_token() == ",":
                output_str += self._validate_token_and_advance({","}, ",", new_offset)
                continue
            output_str += self._compile_expression(new_offset, {",", ")"})

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def _compile_expression(self, current_offset, stop_chars):
        """
        Compiles an expression.
        :param current_offset: (str) tab for parent tag
        :param stop_char: {str} set of characters that ends expression
        :return: (str) xml
        """
        current_tag = "expression"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        if self.tokenizer.current_token() != self:
            output_str += self._compile_term(new_offset)
            # check for other terms
            while self.tokenizer.current_token() not in stop_chars:
                # expect op
                output_str += self._validate_token_and_advance(TERM_OPS, "operator", new_offset)
                # followed by a term
                output_str += self._compile_term(new_offset)

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def _compile_term(self, current_offset):
        """
        Compiles a term.

        If the current token is an identifer,
            may be a variable, array entry, or subroutine call

        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "term"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        # Unambigious cases 1-4
        # (1) integer or string constant type, (2) keyword constant
        if (self.tokenizer.current_type() in {INTEGER_CONSTANT_TAG, STRING_CONSTANT_TAG}) \
            or (self.tokenizer.current_token() in KEYWORD_CONSTANT):
            output_str += new_offset + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()
        # (3) unary operator followed by term
        elif self.tokenizer.current_token() in UNARY_OP:
            # write operator
            output_str += new_offset + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()
            output_str += self._compile_term(new_offset)
        # (4) if char is "(" then expect: ( expression )
        elif self.tokenizer.current_token() == "(":
            # write (
            output_str += new_offset + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()
            output_str += self._compile_expression(new_offset, {")"})
            # write )
            output_str += new_offset + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()
        # otherwise need to distinguish between:
        #  variable, an array entry, and a subroutine call
        else:
            # expect an identifier
            if self.tokenizer.current_type() != IDENTIFIER_TAG:
                raise ValueError(f"Expecting identifer, actual {self.tokenizer.current_type()}")
            # look ahead
            next_token, _, _ = self.tokenizer.look_ahead_token()
            # subroutine
            if next_token in {"(", "."}:
                output_str += self._compile_subroutine_call(new_offset)
            # variable name OR array entry
            else:
                output_str += self._validate_type_and_advance({IDENTIFIER_TAG},
                                                              "identifier", new_offset)
                # array entry
                if self.tokenizer.current_token() == "[":
                    # write [
                    output_str += new_offset + self.tokenizer.current_tag() + "\n"
                    self.tokenizer.next()
                    # expression
                    output_str += self._compile_expression(new_offset, {"]"})
                    # write ]
                    output_str += new_offset + self.tokenizer.current_tag() + "\n"
                    self.tokenizer.next()

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    """
    Helpers methods
    """
    def _validate_and_advance_helper(self, source, target, error_message_input, offset):
        """
        Helper for validate_type_and_advance and validate_token_and_advance
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
                        f"({self.tokenizer.current_type()}) " \
                        f"{self.tokenizer.current_token()}." \
                        f" Current pointer value: {self.tokenizer.get_value_of_pointer()}"

        raise ValueError(error_message)

    def _validate_type_and_advance(self, target, error_message_input, offset):
        """
        Validates current token type
            If valid:
                return xml tag and advance tokenizer
            Otherwise raise error
        :param source: (str) token or type to compare
        :param target: {str} set of expected values
        :param error_message_input: (str) description of target values
        :param offset: (str) tab offset
        :return: (str) xml output for current token
        """
        return self._validate_and_advance_helper(self.tokenizer.current_type(),
                                                 target, error_message_input, offset)

    def _validate_token_and_advance(self, target, error_message_input, offset):
        """
        Validates current token
            If valid:
                return xml tag and advance tokenizer
            Otherwise raise error
        :param target: {str} set of expected values
        :param error_message_input: (str) description of target values
        :param offset: (str) tab offset
        :return: (str) xml output for current token
        """
        return self._validate_and_advance_helper(self.tokenizer.current_token(),
                                                 target, error_message_input, offset)

    def _compile_var_list(self, offset):
        """"
        Compiles pattern:
        type varName (,varName)*;

        Helper for classVarDec and varDec
        :param offset: (str) tab offset
        """
        output_str = ""
        # expect a variable type (either a keyword or identifier)
        output_str += self._validate_type_and_advance({KEYWORD_TAG, IDENTIFIER_TAG},
                                                      "keyword or identifier", offset)
        # expect at least one variable name
        output_str += self._validate_type_and_advance({IDENTIFIER_TAG}, "variable name",
                                                      offset)
        # optional additional variable names
        while self.tokenizer.current_token() != ";":
            if self.tokenizer.current_token() == ",":
                output_str += self._validate_token_and_advance({","}, ",", offset)
                continue
            if self.tokenizer.current_type() == IDENTIFIER_TAG:
                output_str += self._validate_type_and_advance({IDENTIFIER_TAG}, "variable name",
                                                              offset)
            else:
                raise ValueError(
                    f"Expecting variable name, actual: {self.tokenizer.current_token()}")
        # guaranteed to be ;
        output_str += offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()
        return output_str

    def _compile_subroutine_call(self, offset):
        """
        Compiles pattern
        subroutineName '(' expressionList ')' OR
        ( className | varName) '.' subroutineName '(' expressionList ')'
        Helper function for do statment and term
        :param offset:
        :return:
        """
        output_str = ""
        # expect a subroutine name OR (class or variable name)
        output_str += self._validate_type_and_advance({IDENTIFIER_TAG}, "identifier",
                                                      offset)
        # if previous token was a class or variable name
        # next tokens should be "." and a subroutine name
        if self.tokenizer.current_token() == ".":
            output_str += offset + self.tokenizer.current_tag() + "\n"
            self.tokenizer.next()
            output_str += self._validate_type_and_advance({IDENTIFIER_TAG}, "identifier",
                                                          offset)
        # expect "(", followed by an expression list, and ")"
        output_str += self._validate_token_and_advance({"("}, "(", offset)
        output_str += self._compile_expression_list(offset)
        # guaranteed to be )
        output_str += offset + self.tokenizer.current_tag() + "\n"
        self.tokenizer.next()

        return output_str
