"""
Symbol Table Module
"""

STATIC_KIND = "static"
FIELD_KIND = "field"
ARG_KIND = "arg"
LOCAL_KIND = "local"
FIRST_KIND_INDEX = 0

DECLARING = "declaring"
USING = "using"


class SymbolTable:
    """
    Identifier table
    """

    def __init__(self):
        self.__class_table = SingleTable()
        self.__subroutine_table = SingleTable()

    def new_subroutine(self):
        """
        Create empty \table for a new subroutine
        :return: NA, overwrite self.__subroutine_table
        """
        self.__subroutine_table = SingleTable()

    def contains(self, token):
        """
        :param token: (str) identifier name
        :return: true if either table contains token
        """
        return self.__class_table.contains(token) or \
               self.__subroutine_table.contains(token)

    """
    Getters
    """
    def get_kind(self, token):
        """
        Get kind for token
        :param token: (str) identifier name
        :return: (str) kind
        """
        if self.__subroutine_table.contains(token):
            return self.__subroutine_table.get_kind(token)
        if self.__class_table.contains(token):
            return self.__class_table.get_kind(token)
        raise KeyError(f"Symbol table does not contain {token}")

    def get_index(self, token):
        """
        Get index for token
        :param token: (str) identifier name
        :return: (int) index
        """
        if self.__subroutine_table.contains(token):
            return self.__subroutine_table.get_index(token)
        if self.__class_table.contains(token):
            return self.__class_table.get_index(token)
        raise KeyError(f"Symbol table does not contain {token}")

    def get_type(self, token):
        """
        Get token type, e.g. : int, boolean, class
        :param token: (str) identifier name
        :return: (str) type
        """
        if self.__subroutine_table.contains(token):
            return self.__subroutine_table.get_type(token)
        if self.__class_table.contains(token):
            return self.__class_table.get_type(token)
        raise KeyError(f"Symbol table does not contain {token}")

    def get_num_class_fields(self):
        """
        Get the number of field variables for the class
        :return: (int)
        """
        return self.__class_table.get_number_of_field_variables()

    def get_class_table(self):
        """
        Get class symbol table
        :return: (SingleTable)
        """
        return self.__class_table

    def get_subroutine_table(self):
        """
        Get subroutine symbol table
        :return: (SingleTable)
        """
        return self.__subroutine_table

    def __str__(self):
        """
        :return: (str) representation of Symbol Table
        """
        return "*** class\n" \
                f"{self.__class_table}\n" \
                "*** subroutine\n" \
                f"{self.__subroutine_table}\n"


class SingleTable:
    """
    Represents a single symbol table

    self.__table: dict with key (str), value (Row)
    """
    def __init__(self):
        self.__table = {}
        self.__next_static_index = FIRST_KIND_INDEX
        self.__next_field_index = FIRST_KIND_INDEX
        self.__next_arg_index = FIRST_KIND_INDEX
        self.__next_var_index = FIRST_KIND_INDEX

    def get_number_of_field_variables(self):
        """
        Get the number of field variables in the table
        :return: (int)
        """
        # index starts at 0
        return self.__next_field_index

    def contains(self, token):
        """
        :param token: (str) identifier name
        :return: (boolean) true  if table contains token
        """
        return token in self.__table

    def get_kind(self, token):
        """
        :param token: (str) identifier name
        :return: (str) kind
        """
        return self.__table[token].get_kind()

    def get_index(self, token):
        """
        :param token: (str) identifier name
        :return: (int) index
        """
        return self.__table[token].get_identifier_number()

    def get_type(self, token):
        """
        :param token: (str) identifier name
        :return: (str) type (int, boolean, class)
        """
        return self.__table[token].get_type()

    def add_row(self, new_row):
        """
        Add row to the table
        :param new_row: (Row) new row
        :return: NA, update self.table
        """
        identifier_name = new_row.get_name()
        if identifier_name in self.__table:
            raise KeyError(f"Table already contains {identifier_name}")

        identifier_kind = new_row.get_kind()
        if identifier_kind == STATIC_KIND:
            new_row.set_identifier_number(self.__next_static_index)
            self.__next_static_index += 1
        elif identifier_kind == FIELD_KIND:
            new_row.set_identifier_number(self.__next_field_index)
            self.__next_field_index += 1
        elif identifier_kind == ARG_KIND:
            new_row.set_identifier_number(self.__next_arg_index)
            self.__next_arg_index += 1
        elif identifier_kind == LOCAL_KIND:
            new_row.set_identifier_number(self.__next_var_index)
            self.__next_var_index += 1
        else:
            raise ValueError(f"Invalid identifier kind: {identifier_kind}")

        self.__table[identifier_name] = new_row

    def get_row(self, identifier_name):
        """
        Get row associated with identifier
        :param identifier_name: (str) identifier name
        :return: (Row)
        """
        if identifier_name in self.__table:
            return self.__table[identifier_name]
        return None

    def __str__(self):
        """
        :return: representation of table
        """
        return f"{self.__table}"

    def __repr__(self):
        """
        :return: (str) representation of table
        """
        return self.__str__()


class Row:
    """
    Represents a row in a symbol table
    """
    def __init__(self, name, identifier_type, kind, use):
        """

        :param name: (str) identifier name
        :param type: (str) identifier type (int, boolean, class)
        :param kind: (str) static, field, arg, var
        """
        self.__name = name
        self.__identifier_type = identifier_type
        self.__kind = kind
        self.__identifier_number = None
        self.__use = use

    def set_identifier_number(self, identifier_number):
        """
        Set identifier number
        :param identifier_number: (int)
        :return: NA, update self.__identifier_number
        """
        self.__identifier_number = identifier_number

    """
    Getters
    """
    def get_name(self):
        """
        :return: (str) identifier name
        """
        return self.__name

    def get_type(self):
        """
        :return: (str) identifier type, e.g. int, boolean, char, class type
        """
        return self.__identifier_type

    def get_kind(self):
        """
        :return: (str) static, field, arg, or var
        """
        return self.__kind

    def get_identifier_number(self):
        """
        :return: (int) index number
        """
        return self.__identifier_number

    def get_use(self):
        """
        :return: (str) use: declaring or using
        """
        return self.__use

    def __str__(self):
        """
        :return: (str) representation of row
        """
        return f"*** {self.__name}; " \
               f"type: {self.__identifier_type}; " \
               f"kind: {self.__kind}; " \
               f"index: {self.__identifier_number}; " \
               f"use: {self.__use}\n"

    def __repr__(self):
        """
        :return: (str) representation of row
        """
        return self.__str__()
