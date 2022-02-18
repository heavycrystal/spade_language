import sys
import re
import pprint

spade_operators = [ "+", "-", "×", "÷", "/", "&", "|", "^", "√", "=", "!", "~", "#", ">", "<", "[", "]", "←", "→", "⚠", ">=", "<=", "=="]
spade_keywords = [ "sow", "with", "reap", "of", "here", "lies", "is", "harvest", "from", "day", "until", "eternally", "every", "days", "today", "⚠", "fresh?", "rotten", "unearth", "bury", "engrave", "on", "stdout", "stderr", "i64", "u64", "f64", "b8", "b1", "c32", "c∞", "file", "❌", "⭕"]

def parse_fail(error: str, line_index: int):
    print(error)
    print("Parsing failed at line #", line_index)
    exit(1)

def print_hex(token_id: int):
    return str.format("0x{:02x}", token_id)

def print_token(word: str, line_index: int):
    if is_integer_constant(word):
        print(('\t'*4).join([ print_hex(129), "INT_CONSTANT", word]))
    elif is_float_constant(word):
        print(('\t'*4).join([ print_hex(130), "FP_CONSTANT", word]))
    elif is_keyword(word):
        print(('\t'*4).join([ print_hex(spade_keywords.index(word)), "SPADE_KEYWORD", word]))
    elif is_valid_variable_name(word):
        print(('\t'*4).join([ print_hex(128), "IDENTIFIER", word]))
    elif is_operator(word):
        print(('\t'*4).join([ print_hex(64 + spade_operators.index(word)), "SPADE_OPERATOR", word]))
    else:
        split_word = is_expr(word)
        for word in split_word:
            print_token(word, line_index)

def is_integer_constant(word: str):
    try:
        int(word, base = 0)
    except ValueError:
        return False
    return True

def is_float_constant(word: str):
    try:
        float(word)
    except ValueError:
        return False
    return True

def is_keyword(word: str):
    if word in spade_keywords:
        return True
    return False

def is_valid_variable_name(word: str):
    if len([ character for character in list(word) if character in spade_operators ]) > 0:
        return False
    return True

def is_operator(word: str):
    if word in spade_operators:
        return True
    return False

def is_expr(word: str):
    split_word = [ i for i in re.split("(>\=)|(<\=)|(>)|(<)|(\=\=)|(\+)|(-)|(×)|(÷)|(\/)|(&)|(\|)|(\^)|(√)|(\=)|(\!)|(~)|(#)|(←)|(→)|(\[)|(\])", word) if i is not None and len(i) > 0 ]
    return split_word

input_file_lines = list(map(lambda line: line.split(), open(sys.argv[-1], "r").readlines()))

print("\n\nTOKEN_ID\t\t\tTOKEN_TYPE\t\t\t\tTOKEN CONTENTS")

for line_index, line in enumerate(input_file_lines):
    # handling struct enclosures as well as empty lines.
    if len(line) == 0 or "__________" in line or "|__________" in line:
        continue
    if line[0][0] == "⚠":
        continue
    if line[0] == "|":
        line = line[1:]
    word_index = 0
    while word_index < len(line):
        if line[word_index][0] == "\"":
            string_constant =  ""
            while word_index < len(line) and line[word_index][-1] != "\"":
                string_constant = string_constant + " " +  line[word_index]
                word_index = word_index + 1
            if word_index == len(line):
                parse_fail("Error parsing, string constant not terminated.")
            else:
                string_constant = string_constant + " " +  line[word_index][:-1]
                string_constant = string_constant.strip()
                print(('\t'*4).join([ print_hex(131), "STRING_CONSTANT", string_constant[1:] ]))
        else:
            print_token(line[word_index], line_index)
        word_index = word_index + 1