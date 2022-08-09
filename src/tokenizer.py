"""
Tokenizer Module
"""
import re
from grammar_utility import create_tag, \
    KEYWORD_TAG, IDENTIFIER_TAG, SYMBOL_TAG, STRING_CONSTANT_TAG, INTEGER_CONSTANT_TAG, \
    SYMBOLS, KEYWORDS


class Tokenizer:
    """
    Tokenizes jack code
        Pad operators with whitespace
        Tag tokens
    """

    REGEX_PATTERN = r'\s*([*+-/&|<>~.,();{}:\"\[\]])\s*'
    REGEX_PATTERN_STRING_LITERAL = r'["][^"]+["]'
    STRING_LITERAL_SUB = "_STRING_LITERAL_"

    def __init__(self, input_string):
        """
        Construct an instance of tokenizer
        :param input_string: (str) jack code (comments removed)
        """

        self.__input_string = input_string  # original jack code
        self.__string_literals = None  # list of string literals
        self.__padded_string = None  # white space padded operators (with string literals replaced)
        self.__token_type_list = None  # list of tuples (str: token, str: type, str: tags)
        self.__xml = ""

        self._find_string_literals()
        self._replace_string_literals()
        self._pad_operators()

        self.__tokens = self.__padded_string.split()
        self._tag_tokens()

        self.__token_pointer = None
        self.__current_token = None
        self.__current_type = None
        self.__current_xml = None

    def next(self):
        """
        Advance token pointer
        :return: NA, updates self._token_pointer
        """
        self.__token_pointer = 0 if self.__token_pointer is None else (self.__token_pointer + 1)
        if self.__token_pointer >= len(self.__token_type_list):
            self.__token_pointer -= 1
            raise ValueError("Reached end of token input")
        self.__current_token, self.__current_type, self.__current_xml = \
            self.__token_type_list[self.__token_pointer]

    def current_token(self):
        """
        Return current token
        :return: (str) token
        """
        return self.__current_token

    def current_type(self):
        """
        Return current token type
        :return: (str) token type
        """
        return self.__current_type

    def current_tag(self):
        """
        Return xml for current token
        :return: (str) xml
        """
        return self.__current_xml

    def _find_string_literals(self):
        """
        Finds string literals
        :return: NA, updates self.__string_literals
        """
        self.__string_literals = re.findall(Tokenizer.REGEX_PATTERN_STRING_LITERAL,
                                            self.__input_string)

    def _replace_string_literals(self):
        """
        Replace string literals with STRING_LITERAL_SUB
        :return: NA, updates self.__padded_string
        """
        self.__padded_string = re.sub(Tokenizer.REGEX_PATTERN_STRING_LITERAL,
                                      " " + Tokenizer.STRING_LITERAL_SUB + " ",
                                      self.__input_string)

    def _pad_operators(self):
        """
        Pad operators with whitespace
        :return: (str) input str with whitespace padded operators
        """
        self.__padded_string = re.sub(Tokenizer.REGEX_PATTERN,
                                      r' \1 ',
                                      self.__padded_string)

    def _tag_tokens(self):
        """
        Tag each token
        :return: NA, updates self.__xml and self.__token_type_list
        """
        self.__token_type_list = []

        for token in self.__tokens:
            token_type = None
            xml_tag = None
            if token in KEYWORDS:
                xml_tag = create_tag(KEYWORD_TAG, token)
                token_type = KEYWORD_TAG
            elif token in SYMBOLS:
                token = "&lt;" if token == "<" else ("&gt;" if token == ">" else ("&amp;" if token == "&" else token))
                xml_tag = create_tag(SYMBOL_TAG, token)
                token_type = SYMBOL_TAG
            elif token == Tokenizer.STRING_LITERAL_SUB:
                string_literal = self.__string_literals.pop(0)
                xml_tag = create_tag(STRING_CONSTANT_TAG, string_literal[1:-1])
                token_type = STRING_CONSTANT_TAG
            elif token[0].isdigit():
                try:
                    _ = int(token)
                    xml_tag = create_tag(INTEGER_CONSTANT_TAG, token)
                    token_type = INTEGER_CONSTANT_TAG
                except ValueError:
                    raise ValueError(f"Invalid identifier: {token}")
            else:
                xml_tag = create_tag(IDENTIFIER_TAG, token)
                token_type = IDENTIFIER_TAG

            self.__xml += xml_tag + "\n"
            self.__token_type_list.append((token, token_type, xml_tag))

    """
    Getters
    """
    def get_input_str(self):
        return self.__input_string

    def get_string_literals_list(self):
        return self.__string_literals

    def get_padded_str(self):
        return self.__padded_string

    def get_tokens(self):
        return self.__tokens

    def get_token_type_list(self):
        return self.__token_type_list

    def get_xml(self):
        return "<tokens>\n" + self.__xml + "</tokens>\n"
