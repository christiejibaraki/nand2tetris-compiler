"""
Scratchpad for testing regex
"""
import re

# Todo
# minus, divide, boolean operators, commas
REGEX_PATTERN = r'\s*([*+.();{}:\"\[\]])\s*'

tests = ["let a = Array.new(length);",
         """while (i < length) {
            let a[i] = Keyboard.readInt("ENTER THE NEXT NUMBER: ");
            let i = i + 1;
            }"""]

for test in tests:
    print(re.sub(REGEX_PATTERN, r' \1 ', test))

# REGEX_PATTERN_STRING_LITERAL = r'["][\w\s\S]+["]'
REGEX_PATTERN_STRING_LITERAL = r'["][^"]+["]'
test_string = """let length = Keyboard.readInt("HOW MANY NUMBERS? ");\nlet a = Array.new(length); "help" """
string_lit_lst = re.findall(REGEX_PATTERN_STRING_LITERAL, test_string)
print(string_lit_lst)
temp_str = re.sub(REGEX_PATTERN_STRING_LITERAL, " _STRING_LITERAL_ ", test_string)
temp_str = re.sub(REGEX_PATTERN, r' \1 ', temp_str)
print(temp_str)
for x in string_lit_lst:
    temp_str = re.sub("_STRING_LITERAL_", x[1:-1], temp_str, count=1)
print(temp_str)
