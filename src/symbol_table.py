"""
Symbol Table Module
"""

STATIC_KIND = "static"
FIELD_KIND = "field"
ARG_KIND = "arg"
VAR_KIND = "kind"
FIRST_KIND_INDEX = 1


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

    """
    Getters
    """
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
        elif identifier_kind == VAR_KIND:
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


class Row:
    """
    Represents a row in a symbol table
    """
    def __init__(self, name, identifier_type, kind):
        """

        :param name: (str) identifier name
        :param type: (str) identifier type (int, boolean, class)
        :param kind: (str) static, field, arg, var
        """
        self.__name = name
        self.__identifier_type = identifier_type
        self.__kind = kind
        self.__identifier_number = None

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
        return self.__type

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
