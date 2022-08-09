"""
Lexical elements of Jack language
"""

KEYWORD_TAG = "keyword"
IDENTIFIER_TAG = "identifier"
SYMBOL_TAG = "symbol"
STRING_CONSTANT_TAG = "stringConstant"
INTEGER_CONSTANT_TAG = "integerConstant"

"""
Constants for compilation engine
"""
SUBROUTINE_DEC_SET = {"constructor", "function", "method"}
SUBROUTINE_OR_CLASS_END = {"constructor", "function", "method", "}"}
STATEMENT_SET = {"let", "if", "while", "do", "return"}
STATEMENT_OR_ROUTINE_END = {"let", "if", "while", "do", "return", "}"}
TERM_OPS = {'+', '-', '*', '/', '&', '|', '<', '>', '=', "&lt;", "&gt;", "&amp;"}
KEYWORD_CONSTANT = {'true', 'false', 'null' , 'this'}
UNARY_OP = {'-', '~'}

SYMBOLS = {'{', '}',
           '(', ')',
           '[', ']',
           '.', ',', ';',
           '+', '-', '*', '/',
           '&', '|', '<', '>', '=', '~'
           }

KEYWORDS = {'class',
            'constructor',
            'function',
            'method',
            'field',
            'static',
            'var',
            'int',
            'char',
            'boolean',
            'void',
            'true',
            'false',
            'null',
            'this',
            'let',
            'do',
            'if',
            'else',
            'while',
            'return'}


def create_tag(tag_type, token):
    """
    Create start and end tags for token
    :param tag_type: (str) tag
    :param token: (str) token tag
    :return: (str) tagged token: "<type> token </type>"
    """
    return f"<{tag_type}> {token} </{tag_type}>"
