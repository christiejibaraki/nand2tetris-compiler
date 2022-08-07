"""
Tokenizer Module
"""
import re
from grammar import create_tag, \
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
        :param input_string: (Str) jack code (comments removed)
        """

        self.__input_string = input_string  # original jack code
        self.__string_literals = None  # list of string literals
        self.__padded_string = None  # white space padded operators (with string literals replaced)
        self.__xml = "<tokens>\n"

        self._find_string_literals()
        self._replace_string_literals()
        self._pad_operators()

        self.__tokens = self.__padded_string.split()
        self._tag_tokens()

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
        :return: NA, updates self.__xml
        """
        for token in self.__tokens:
            if token in KEYWORDS:
                self.__xml += create_tag(KEYWORD_TAG, token)
            elif token in SYMBOLS:
                token = "&lt;" if token == "<" else ("&gt;" if token == ">" else ("&amp;" if token == "&" else token))
                self.__xml += create_tag(SYMBOL_TAG, token)
            elif token == Tokenizer.STRING_LITERAL_SUB:
                string_literal = self.__string_literals.pop(0)
                self.__xml += create_tag(STRING_CONSTANT_TAG, string_literal[1:-1])
            elif token[0].isdigit():
                try:
                    _ = int(token)
                    self.__xml += create_tag(INTEGER_CONSTANT_TAG, token)
                except ValueError:
                    raise ValueError(f"Invalid identifier: {token}")
            else:
                self.__xml += create_tag(IDENTIFIER_TAG, token)
            self.__xml += "\n"

        self.__xml += "</tokens>\n"


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

    def get_xml(self):
        return self.__xml
