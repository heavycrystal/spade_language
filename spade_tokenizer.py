import sys
import re

spade_operators = [ "+", "-", "×", "÷", "/", "&", "|", "^", "√", "=", "!", "~", "#", ">", "<", "[", "]", "←", "→", "⚠", "≥", "≤", "=", ",", "&&", "||"]
spade_keywords = [ "sow", "with", "reap", "of", "here", "lies", "is", "harvest", "from", "until", "eternally", "every", "⚠", "fresh?", "rotten", "kill", "skip", "supply", "unearth", "bury", "engrave", "on", "stdout", "stderr", "i64", "u64", "f64", "i32", "u32", "f32", "b8", "b1", "c32", "c∞", "file", "❌", "⭕" ]

def parse_fail(error: str, line_index: int):
    print(error)
    print("Parsing failed at line #", line_index)
    exit(1)

def print_hex(token_id: int):
    return str.format("0x{:02x}", token_id)

def print_token(word: str, line_index: int):
    if is_integer_constant(word):
        print(('\t' * 4).join([str(line_index + 1), print_hex(129), "INT_CONSTANT", word]))
    elif is_float_constant(word):
        print(('\t' * 4).join([str(line_index + 1), print_hex(130), "FP_CONSTANT", word]))
    elif is_keyword(word):
        print(('\t' * 4).join([str(line_index + 1), print_hex(spade_keywords.index(word)), "SPADE_KEYWORD", word]))
    elif is_valid_variable_name(word):
        print(('\t' * 4).join([str(line_index + 1), print_hex(128), "IDENTIFIER", word]))
    elif is_operator(word):
        print(('\t' * 4).join([str(line_index + 1), print_hex(64 + spade_operators.index(word)), "SPADE_OPERATOR", word]))
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
    split_word = list(filter(None, re.split("(≤)|(≥)|(>)|(<)|(&&)|(\|\|)|(\+)|(-)|(×)|(÷)|(\/)|(&)|(\|)|(\^)|(√)|(\=)|(≠)|(\!)|(~)|(#)|(←)|(→)|(\[)|(\])|(,)", word)))
    return split_word

input_file_lines = list(map(lambda line: list(filter(None, re.split("\n|([ \t]+)", line))), open(sys.argv[-1], "r", encoding = 'utf8').readlines()))

print("\n\nLINE_NUMBER\t\t\tTOKEN_ID\t\t\tTOKEN_TYPE\t\t\t\tTOKEN CONTENTS")

for line_index, line in enumerate(input_file_lines):
    # handling struct enclosures as well as empty lines.
    if len(line) == 0 or "__________" in line or "|__________" in line:
        continue
    elif line[0][0] == "⚠":
        continue
    elif line[0] == "|":
        line = line[1:]
    
    word_index = 0
    while word_index < len(line):
        if ' ' in line[word_index]:
            word_index = word_index + 1
            continue
        if len(line[word_index]) > 1 and line[word_index][-1] == "\"" and line[word_index][0] != "\"":
            parse_fail("Error parsing, (\") is an illegal character.\nLine: " + ''.join(line), line_index + 1)
        elif line[word_index][0] == "\"":
            if line[word_index][-1] == "\"" and len(line[word_index]) > 1 and line[word_index][-2] != "\\":
                string_constant = line[word_index]
            else:
                string_constant = line[word_index]
                word_index = word_index + 1
                while word_index < len(line) and (line[word_index][-1] != "\"" or (len(line[word_index]) > 1 and line[word_index][-2] == "\\")):
                    string_constant = string_constant + line[word_index]
                    word_index = word_index + 1
                if word_index == len(line):
                    print(string_constant, len(string_constant))
                    parse_fail("Error parsing, string constant is unterminated.\nLine: " + ''.join(line), line_index + 1)
                string_constant = string_constant + line[word_index]
                if string_constant.count("\"") == 1:
                    print(string_constant, len(string_constant))
                    parse_fail("Error parsing, string constant is unterminated.\nLine: " + ''.join(line), line_index + 1)      
            print(('\t'*4).join([ str(line_index + 1), print_hex(131), "STRING_CONSTANT", string_constant.strip()[1:-1] ]))
            word_index = word_index + 1
        else:
            print_token(line[word_index], line_index)
        word_index = word_index + 1


