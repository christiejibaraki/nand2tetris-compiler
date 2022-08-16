"""
Compilation Engine Module
"""
from tokenizer import Tokenizer
from grammar_utility import \
    KEYWORD_TAG, IDENTIFIER_TAG, STRING_CONSTANT_TAG, INTEGER_CONSTANT_TAG
from grammar_utility import SUBROUTINE_OR_CLASS_END, SUBROUTINE_DEC_SET, \
    STATEMENT_OR_ROUTINE_END, TERM_OPS, KEYWORD_CONSTANT, UNARY_OP
from symbol_table import SymbolTable, Row, DECLARING, ARG_KIND, LOCAL_KIND
from vm_writer import VMWriter, \
    POINTER_SEGMENT, ARGUMENT_SEGMENT, CONSTANT_SEGMENT, TEMP_SEGMENT, THAT_SEGMENT

OFFSET_CHAR = "  "


class CompilationEngine:
    """
    Effects the actual compilation output.
        Gets its input from a JackTokenizer and
        outputs VM commands
        and XML that reflects syntactic structure of program
    """

    def __init__(self, input_str):
        """
        :param input_str: (str) jack code (comments removed)
        """
        self.__tokenizer = Tokenizer(input_str)
        self.__tokenizer.next()
        if not self.__tokenizer.current_token() == "class":
            error_message = "Syntax Error: Expecting keyword \"class\", " \
                            f"actual token: {self.__tokenizer.current_token()}"
            raise ValueError(error_message)

        self.__symbol_table = SymbolTable()
        self.__vm_writer = VMWriter()

        # for vm writer
        self.__current_index_while = 0
        self.__current_index_if = 0
        self.__current_class = None
        self.__current_subroutine_name = None
        self.__current_subroutine_type = None
        self.__current_subroutine_return_type = None
        self.__current_subroutine_n_locals = None  # number of local variables
        self.__current_subroutine_args = None

        self.__xml_output = self._compile_class()

    def get_vm_command_output(self):
        """
        Returns the vm commands constructed by the compilation engine
        :return: (str) vm commands
        """
        return self.__vm_writer.get_output()

    def get_xml_output(self):
        """
        Returns the xml output constructed by the compilation engine
        :return: (str) xml representing parse tree
        """
        return self.__xml_output

    def get_symbol_table(self):
        """
        Returns symbol table
        :return: (SymbolTable)
        """
        return self.__symbol_table

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
        self.__current_class = self.__tokenizer.current_token()
        output_str += self._validate_type_and_advance(
            {IDENTIFIER_TAG}, "identifier", current_offset)

        # expect {
        output_str += self._validate_token_and_advance({"{"}, "{", current_offset)

        # optional class variable declarations
        while not self.__tokenizer.current_token() in SUBROUTINE_OR_CLASS_END:
            if self.__tokenizer.current_token() in {"static", "field"}:
                output_str += self._compile_class_var_dec(current_offset)

        # optional subroutines
        while self.__tokenizer.current_token() != "}":
            if self.__tokenizer.current_token() in SUBROUTINE_DEC_SET:
                output_str += self._compile_subroutine(current_offset)

        # expect "}"
        temp = "}"
        if self.__tokenizer.current_token() != "}":
            raise ValueError(f"Expecting {temp}, actual {self.__tokenizer.current_token()}")

        output_str += current_offset + self.__tokenizer.current_tag() + "\n"
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
        output_str += new_offset + self.__tokenizer.current_tag() + "\n"
        static_or_field_kind = self.__tokenizer.current_token()
        self.__tokenizer.next()
        # type varName (,varName)*
        # helper functions add variables to class symbol table
        output_str += self._compile_var_list(new_offset, static_or_field_kind, True)

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def _reset_subroutine_properties(self):
        """
        Reset field related to subroutine
        :return: NA
        """
        self.__current_subroutine_name = None
        self.__current_subroutine_type = None
        self.__current_subroutine_return_type = None
        self.__current_subroutine_n_locals = 0
        self.__symbol_table.new_subroutine()

    def _compile_subroutine(self, current_offset):
        """
        Compiles a complete method, function, or constructor
        :param current_offset: (str) tab for parent tag
        :return: (str) xml for class var dec
        """
        # init new subroutine
        self._reset_subroutine_properties()

        current_tag = "subroutineDec"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        # guaranteed to be constructor, function, or method
        self.__current_subroutine_type = self.__tokenizer.current_token()
        if self.__current_subroutine_type == "method":
            # if subroutine is a method, add this to subroutine symbol table
            self._add_var_to_symbol_table("this", self.__current_class, ARG_KIND, DECLARING, False)

        output_str += new_offset + self.__tokenizer.current_tag() + "\n"
        self.__tokenizer.next()

        # expect void or type (int, char, boolean, classname)
        self.__current_subroutine_return_type = self.__tokenizer.current_token()
        output_str += self._validate_type_and_advance({KEYWORD_TAG, IDENTIFIER_TAG},
                                                      "keyword or identifier", new_offset)

        # expect a subroutine name
        self.__current_subroutine_name = self.__tokenizer.current_token()
        self.__vm_writer.write_comment(self.__current_subroutine_name +
                                       f" ; return: {self.__current_subroutine_return_type}")
        output_str += self._validate_type_and_advance({IDENTIFIER_TAG}, "subroutine name",
                                                      new_offset)
        # expect (
        output_str += self._validate_token_and_advance({"("}, "(", new_offset)
        # parameter list, helper function adds params to subroutine symbol table
        output_str += self._compile_paramater_list(new_offset)
        # expect )
        output_str += self._validate_token_and_advance({")"}, ")", new_offset)

        # expect {
        # subroutineBody
        if self.__tokenizer.current_token() == "{":
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

        while self.__tokenizer.current_token() != ")":
            if self.__tokenizer.current_token() == ",":
                output_str += self._validate_token_and_advance({","}, ",", new_offset)
                continue
            var_type = self.__tokenizer.current_token()
            output_str += self._validate_type_and_advance({KEYWORD_TAG, IDENTIFIER_TAG},
                                                          "var type", new_offset)
            var_name = self.__tokenizer.current_token()
            output_str += self._validate_type_and_advance({IDENTIFIER_TAG},
                                                          "var name", new_offset)

            self._add_var_to_symbol_table(var_name, var_type, ARG_KIND, DECLARING, False)

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
        output_str += new_offset + self.__tokenizer.current_tag() + "\n"
        self.__tokenizer.next()

        # compile any variable declarations, add to subroutine symbol table
        while self.__tokenizer.current_token() not in STATEMENT_OR_ROUTINE_END:
            output_str += self._compile_subroutine_var_dec(new_offset)

        # vm command to declare a subroutine after local variables are counted
        self.__vm_writer.write_function_command(
            f"{self.__current_class}.{self.__current_subroutine_name}",
            self.__current_subroutine_n_locals)

        # if method, first arg is reference to the instance
        # (makes memory location THIS point at instance of object in the heap)
        if self.__current_subroutine_type == "method":
            self.__vm_writer.write_push_command(ARGUMENT_SEGMENT, 0)  # first arg is always this
            self.__vm_writer.write_pop_command(POINTER_SEGMENT, 0)  # pop into memory location THIS
        # if constructor, allocate memory for the object on the heap
        # based num of object fields
        elif self.__current_subroutine_type == "constructor":
            self.__vm_writer.write_push_command(CONSTANT_SEGMENT,
                                                self.__symbol_table.get_num_class_fields())
            self.__vm_writer.write_call_command("Memory.alloc", 1)  # returns location of instance on heap
            self.__vm_writer.write_pop_command(POINTER_SEGMENT, 0)  # pop into THIS

        # compile any statements
        while self.__tokenizer.current_token() != "}":
            output_str += self._compile_statements(new_offset)

        # guaranteed to be "}"
        output_str += new_offset + self.__tokenizer.current_tag() + "\n"
        self.__tokenizer.next()

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    def _compile_subroutine_var_dec(self, current_offset):
        """
        Compiles a var declaration
        Add variables to subroutine symbol table
        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "varDec"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        # guaranteed to be var
        output_str += new_offset + self.__tokenizer.current_tag() + "\n"
        self.__tokenizer.next()
        # type varName (,varName)*, add variables to subroutine table
        output_str += self._compile_var_list(new_offset, LOCAL_KIND, False)

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

        while self.__tokenizer.current_token() != "}":
            current_token = self.__tokenizer.current_token()
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
        output_str += new_offset + self.__tokenizer.current_tag() + "\n"
        self.__tokenizer.next()
        # subroutine call
        output_str += self._compile_subroutine_call(new_offset)
        # expect ;
        output_str += self._validate_token_and_advance({";"}, ";", new_offset)

        # TODO: not sure if I need to do this elsewhere too. compile_term?
        # no return so pop 0
        self.__vm_writer.write_pop_command(TEMP_SEGMENT, 0)

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
        output_str += new_offset + self.__tokenizer.current_tag() + "\n"
        self.__tokenizer.next()
        # expecting varname, could be name of an array
        is_array = False
        target_var = self.__tokenizer.current_token()
        output_str += self._validate_type_and_advance({IDENTIFIER_TAG}, "identifier",
                                                      new_offset)
        # optional [expression], if array
        if self.__tokenizer.current_token() == "[":
            is_array = True
            output_str += new_offset + self.__tokenizer.current_tag() + "\n"
            self.__tokenizer.next()
            # compile expression and push index of array
            output_str += self._compile_expression(new_offset, {"]"})
            output_str += self._validate_token_and_advance({"]"}, "]", new_offset)
            # push name of array which is address of where array starts
            self.__vm_writer.write_push_command(self.__symbol_table.get_kind(target_var),
                                       self.__symbol_table.get_index(target_var))
            # add index and array start, put it in temp (in case expression also uses THAT)
            self.__vm_writer.write_arithmetic_command("add")
            self.__vm_writer.write_pop_command(TEMP_SEGMENT, 1)

        # vm: push expression on stack
        # expect "="
        output_str += self._validate_token_and_advance({"="}, "=", new_offset)
        # expect expression
        output_str += self._compile_expression(new_offset, {";"})
        # expect ;
        output_str += self._validate_token_and_advance({";"}, ";", new_offset)

        # if target is an array,
        if is_array:
            self.__vm_writer.write_push_command(TEMP_SEGMENT, 1)  # push temp
            self.__vm_writer.write_pop_command(POINTER_SEGMENT, 1)  # pop into THAT
            self.__vm_writer.write_pop_command(THAT_SEGMENT, 0)  # pop compiled expression in THAT
        # if target not array, simple pop into target
        else:
            self.__vm_writer.write_pop_command(self.__symbol_table.get_kind(target_var),
                                       self.__symbol_table.get_index(target_var))

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

        # unique labels
        l1 = self._get_unique_while_label()
        l2 = self._get_unique_while_label()

        # guaranteed to be while
        output_str += new_offset + self.__tokenizer.current_tag() + "\n"
        self.__tokenizer.next()

        # vm: L1
        self.__vm_writer.write_label_command(l1)

        # compile expression
        # expect (
        output_str += self._validate_token_and_advance({"("}, ")", new_offset)
        # expression
        output_str += self._compile_expression(new_offset, {")"})
        # expect )
        output_str += self._validate_token_and_advance({")"}, ")", new_offset)

        # vm: not the expression
        self.__vm_writer.write_arithmetic_command("not")
        # vm: if expression not true jump to L2
        self.__vm_writer.write_if_command(l2)

        # compile statements
        # expect {
        output_str += self._validate_token_and_advance({"{"}, "{", new_offset)
        # optional statements
        output_str += self._compile_statements(new_offset)
        # guaranteed to be }
        output_str += new_offset + self.__tokenizer.current_tag() + "\n"
        self.__tokenizer.next()

        # vm: go back to l1
        self.__vm_writer.write_goto_command(l1)
        # vm: l2
        self.__vm_writer.write_label_command(l2)

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
        output_str += new_offset + self.__tokenizer.current_tag() + "\n"
        self.__tokenizer.next()
        # if not empty return, expression
        if self.__tokenizer.current_token() != ";":
            output_str += self._compile_expression(new_offset, {";"})
        # expect ;
        output_str += self._validate_token_and_advance({";"}, ";", new_offset)

        output_str += current_offset + f"</{current_tag}>" + "\n"

        # write vm_commands
        if self.__current_subroutine_return_type == "void":
            self.__vm_writer.write_void_return()
        else:
            self.__vm_writer.write_return_command()
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

        # unique labels
        l1 = self._get_unique_if_label()
        l2 = self._get_unique_if_label()

        # guaranteed to be if
        output_str += new_offset + self.__tokenizer.current_tag() + "\n"
        self.__tokenizer.next()

        # compile the expression and put it on stack
        # expect (
        output_str += self._validate_token_and_advance({"("}, ")", new_offset)
        # expression
        output_str += self._compile_expression(new_offset, {")"})
        # expect )
        output_str += self._validate_token_and_advance({")"}, ")", new_offset)

        # vm: not the expression - if the expression was true (-1) it is now 0
        self.__vm_writer.write_arithmetic_command("not")
        # vm: jump to l1 if expression not equal to zero (i.e. not true)
        self.__vm_writer.write_if_command(l1)

        # compile statements 1 (for true) and put it on the stack
        # expect {
        output_str += self._validate_token_and_advance({"{"}, "{", new_offset)
        # optional statements
        output_str += self._compile_statements(new_offset)
        # guaranteed to be }
        output_str += new_offset + self.__tokenizer.current_tag() + "\n"
        self.__tokenizer.next()

        # vm: go to l2
        self.__vm_writer.write_goto_command(l2)
        # vm: write label l1 (for expression that wasn't true)
        self.__vm_writer.write_label_command(l1)

        # optional else block (if expression wasn't true)
        # compile statements 2 (for false) and put it on stack
        if self.__tokenizer.current_token() == "else":
            output_str += new_offset + self.__tokenizer.current_tag() + "\n"
            self.__tokenizer.next()
            # expect {
            output_str += self._validate_token_and_advance({"{"}, "{", new_offset)
            # optional statements
            output_str += self._compile_statements(new_offset)
            # guaranteed to be }
            output_str += new_offset + self.__tokenizer.current_tag() + "\n"
            self.__tokenizer.next()

        # vm: write label 2
        self.__vm_writer.write_label_command(l2)

        output_str += current_offset + f"</{current_tag}>" + "\n"
        return output_str

    """
    Expression methods
    """
    def _compile_expression_list(self, current_offset):
        """
        Compiles a (possibly empty) comma separated list of expressions.
        Helper for calling a subroutine

        :param current_offset: (str) tab for parent tag
        :return: (str) xml
        """
        current_tag = "expressionList"
        output_str = current_offset + f"<{current_tag}>" + "\n"
        new_offset = current_offset + OFFSET_CHAR

        # compile expressions until hit ")"
        while self.__tokenizer.current_token() != ")":
            if self.__tokenizer.current_token() == ",":
                output_str += self._validate_token_and_advance({","}, ",", new_offset)
                continue
            self.__current_subroutine_args += 1
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

        if self.__tokenizer.current_token() != self:
            output_str += self._compile_term(new_offset)
            # check for other terms
            while self.__tokenizer.current_token() not in stop_chars:
                # expect op
                operator = self.__tokenizer.current_token()
                output_str += self._validate_token_and_advance(TERM_OPS, "operator", new_offset)
                # followed by a term, which gets put on stack first
                output_str += self._compile_term(new_offset)
                # vm write operator after term
                self.__vm_writer.write_op(operator)

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
        if (self.__tokenizer.current_type() in {INTEGER_CONSTANT_TAG, STRING_CONSTANT_TAG}) \
                or (self.__tokenizer.current_token() in KEYWORD_CONSTANT):
            self.__vm_writer.write_constant_int_string_keyword(
                self.__tokenizer.current_type(), self.__tokenizer.current_token())
            output_str += new_offset + self.__tokenizer.current_tag() + "\n"
            self.__tokenizer.next()
        # (3) unary operator followed by term
        elif self.__tokenizer.current_token() in UNARY_OP:
            # write operator
            unary_operator = self.__tokenizer.current_token()
            output_str += new_offset + self.__tokenizer.current_tag() + "\n"
            self.__tokenizer.next()
            # term gets put on stack first, followed by operator
            output_str += self._compile_term(new_offset)
            self.__vm_writer.write_unary_op(unary_operator)
        # (4) if char is "(" then expect: ( expression )
        elif self.__tokenizer.current_token() == "(":
            # write (
            output_str += new_offset + self.__tokenizer.current_tag() + "\n"
            self.__tokenizer.next()
            output_str += self._compile_expression(new_offset, {")"})
            # write )
            output_str += new_offset + self.__tokenizer.current_tag() + "\n"
            self.__tokenizer.next()
        # otherwise need to distinguish between:
        #  variable, an array entry, and a subroutine call
        else:
            # expect an identifier
            if self.__tokenizer.current_type() != IDENTIFIER_TAG:
                raise ValueError(f"Expecting identifer, actual {self.__tokenizer.current_type()}")
            # look ahead
            next_token, _, _ = self.__tokenizer.look_ahead_token()
            # subroutine
            if next_token in {"(", "."}:
                output_str += self._compile_subroutine_call(new_offset)
            # array entry
            elif next_token == "[":
                target_var = self.__tokenizer.current_token()
                output_str += self._validate_type_and_advance({IDENTIFIER_TAG},
                                                              "identifier", new_offset)
                # push index of array
                # write [
                output_str += new_offset + self.__tokenizer.current_tag() + "\n"
                self.__tokenizer.next()
                # expression
                output_str += self._compile_expression(new_offset, {"]"})
                # write ]
                output_str += new_offset + self.__tokenizer.current_tag() + "\n"
                self.__tokenizer.next()

                # push start of array
                self.__vm_writer.write_push_command(self.__symbol_table.get_kind(target_var),
                                                    self.__symbol_table.get_index(target_var))
                self.__vm_writer.write_arithmetic_command("add")
                self.__vm_writer.write_pop_command(POINTER_SEGMENT, 1)  # put in memory location THAT
                self.__vm_writer.write_push_command(THAT_SEGMENT, 0)  # put it on the stack
            # variable name
            else:
                # push variable
                self.__vm_writer.write_push_command(
                    self.__symbol_table.get_kind(self.__tokenizer.current_token()),
                    self.__symbol_table.get_index(self.__tokenizer.current_token()))
                output_str += self._validate_type_and_advance({IDENTIFIER_TAG},
                                                              "identifier", new_offset)

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
            out = offset + self.__tokenizer.current_tag() + "\n"
            self.__tokenizer.next()
            return out

        error_message = f"Expecting {error_message_input}, actual: " \
                        f"({self.__tokenizer.current_type()}) " \
                        f"{self.__tokenizer.current_token()}." \
                        f" Current pointer value: {self.__tokenizer.get_value_of_pointer()}"

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
        return self._validate_and_advance_helper(self.__tokenizer.current_type(),
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
        return self._validate_and_advance_helper(self.__tokenizer.current_token(),
                                                 target, error_message_input, offset)

    def _compile_var_list(self, offset, var_kind, is_class_var):
        """"
        Compiles pattern:
        type varName (,varName)*;
        Helper for classVarDec and varDec
        Add variables to appropriate symbol table

        :param offset: (str) tab offset
        :param var_kind: (str) static, field, arg, var
        :param is_class_var: (boolean) if true class var, else subroutine var
        """
        output_str = ""
        # expect a variable type (either a keyword or identifier)
        var_type = self.__tokenizer.current_token()
        output_str += self._validate_type_and_advance({KEYWORD_TAG, IDENTIFIER_TAG},
                                                      "keyword or identifier", offset)
        # expect at least one variable name
        self._add_var_to_symbol_table(self.__tokenizer.current_token(),
                                      var_type, var_kind, DECLARING, is_class_var)
        output_str += self._validate_type_and_advance({IDENTIFIER_TAG}, "variable name",
                                                      offset)
        # increment subroutine n local vars
        if not is_class_var:
            self.__current_subroutine_n_locals += 1

        # optional additional variable names
        while self.__tokenizer.current_token() != ";":
            if self.__tokenizer.current_token() == ",":
                output_str += self._validate_token_and_advance({","}, ",", offset)
                continue
            if self.__tokenizer.current_type() == IDENTIFIER_TAG:
                self._add_var_to_symbol_table(self.__tokenizer.current_token(),
                                              var_type, var_kind, DECLARING, is_class_var)
                output_str += self._validate_type_and_advance({IDENTIFIER_TAG}, "variable name",
                                                              offset)
                # increment subroutine n local vars
                if not is_class_var:
                    self.__current_subroutine_n_locals += 1
            else:
                raise ValueError(
                    f"Expecting variable name, actual: {self.__tokenizer.current_token()}")
        # guaranteed to be ;
        output_str += offset + self.__tokenizer.current_tag() + "\n"
        self.__tokenizer.next()
        return output_str

    def _compile_subroutine_call(self, offset):
        """
        Compiles pattern
        subroutineName '(' expressionList ')' OR
        ( className | varName) '.' subroutineName '(' expressionList ')'

        Helper function for do statement AND term

        :param offset: (str) tab offset
        :return: NA
        """
        # for vm writer
        self.__current_subroutine_args = 0

        output_str = ""
        # expect a subroutine name OR (class or variable name)
        name_1 = self.__tokenizer.current_token()
        output_str += self._validate_type_and_advance({IDENTIFIER_TAG}, "identifier",
                                                      offset)
        # if previous token was a class or variable name
        # next tokens should be "." and a subroutine name
        if self.__tokenizer.current_token() == ".":
            output_str += offset + self.__tokenizer.current_tag() + "\n"
            self.__tokenizer.next()
            subroutine_call_name = f"{name_1}.{self.__tokenizer.current_token()}"
            # if name1 is in symbol table, push instance as first arg
            if self.__symbol_table.contains(name_1):
                self.__vm_writer.write_push_command(self.__symbol_table.get_kind(name_1),
                                                    self.__symbol_table.get_index(name_1))
                self.__current_subroutine_args += 1
                # the name of the class followed by the subroutine
                subroutine_call_name = f"{self.__symbol_table.get_type(name_1)}." \
                                       f"{self.__tokenizer.current_token()}"

            output_str += self._validate_type_and_advance({IDENTIFIER_TAG}, "identifier",
                                                          offset)

        # if no ".", a method is called on current instance
        else:
            # push instance as first arg (pointer 0)
            subroutine_call_name = f"{self.__current_class}.{name_1}"
            self.__vm_writer.write_push_command(POINTER_SEGMENT, 0)  # THIS
            self.__current_subroutine_args += 1

        # compile expression list which counts the subroutine args
        # expect "(", followed by an expression list, and ")"
        # puts the arguments on the stack and increments # args
        output_str += self._validate_token_and_advance({"("}, "(", offset)
        output_str += self._compile_expression_list(offset)
        # guaranteed to be )

        # vm: write call the subroutine
        self.__vm_writer.write_call_command(subroutine_call_name, self.__current_subroutine_args)

        output_str += offset + self.__tokenizer.current_tag() + "\n"
        self.__tokenizer.next()

        return output_str

    def _add_var_to_symbol_table(self, name, identifier_type, kind, use, is_class_var):
        """
        Add identifier to symbol table
        :param name: (str) name if identifier
        :param identifier_type: (str) type of identifier (int, boolean, class type)
        :param kind: (str) kind of identifier (static, field)
        :param use: (str) declaring, using
        :param is_class_var: (boolean) if true, update class table,
                            otherwise subroutine table
        :return: NA, update symbol table
        """
        if is_class_var:
            table = self.__symbol_table.get_class_table()
        else:
            table = self.__symbol_table.get_subroutine_table()

        new_row = Row(name, identifier_type, kind, use)
        table.add_row(new_row)

    def _get_unique_if_label(self):
        """
        Create unique label for if statements
        Increment if label index
        :return: (str) unique label
        """
        label = f"{self.__current_class}.{self.__current_subroutine_name}" \
                f"If{self.__current_index_if}"
        self.__current_index_if += 1
        return label

    def _get_unique_while_label(self):
        """
        Create unique label for while statements
        Increment while label index
        :return: (str) unique label
        """
        label = f"{self.__current_class}.{self.__current_subroutine_name}" \
                f"While{self.__current_index_while}"
        self.__current_index_while += 1
        return label
