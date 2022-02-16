import sys
from types import NoneType

input_file_lines = list(map(lambda line: line.split(), open(sys.argv[-1], "r").readlines()))

binary_arithmetic_operators = [ "+", "-", "×", "÷", "/", "&", "|", "^", "&&", "||", "××", "√", " is ", "==" ]
unary_arithmetic_operators = [ "+", "-", "!", "~" ]
symbols = [ "#", "[", "]", "←", "→" ]

# "here lies" and "from day" should be coalesced into a single token later.
type_specifiers = [ "i64", "u64", "f64", "b8", "b1", "c32", "c∞", "file" ]
spade_keyboards = [ "sow", "with", "reap", "of", "here", "lies", "is", "harvest", "from", "day", "until", "eternally", "every", "days", "today", "⚠", "fresh?", "rotten", "unearth", "bury", "engrave", "on", "stdout", "stderr" ]

restricted_characters = [ "+", "-", "×", "÷", "/", "&", "|", "^", "√", "=", "!", "~", "#", "[", "]", "←", "→", ".", "⚠" ]

def parse_fail(error: str | NoneType):
    global line_index

    if error != None:
        print(error)
    print("Parsing failed at line #", line_index)
    exit(1)

def is_integral(word: str):
    try:
        int(word, base = 0)
    except ValueError:
        parse_fail("Error parsing, expected to be integer: " + word)
    return True

def is_valid_variable_name(word: str):
    if (word in type_specifiers) or (word in spade_keyboards) or (len([ character for character in list(word) if character in restricted_characters ]) > 0):
        parse_fail("Error parsing, malformed variable name: " + word)
    try:
        int(word, base = 0)
    except ValueError:
        return True
    parse_fail("Error parsing, variable name is integral: " + word)

def print_tokens(line_words: list):
    word_index = 0
    while word_index < len(line_words):
        if line_words[word_index][0] == "\"":
            string_constant =  ""
            while word_index < len(line_words) and line_words[word_index][-1] != "\"":
                string_constant = string_constant + " " +  line_words[word_index]
                word_index = word_index + 1
            if word_index == len(line_words):
                parse_fail("Error parsing, string constant not terminated.")
            else:
                string_constant = string_constant + " " +  line_words[word_index][:-1]
                string_constant = string_constant.strip()
                print("string constant: ", string_constant[1:])
        elif  line_words[word_index] in spade_keyboards:
            print("keyword: ",  line_words[word_index])
        elif line_words[word_index] in type_specifiers:
            print("type specifier: ", line_words[word_index])
        else:
            try:
                int(line_words[word_index], base = 0)
                print("integer constant: ", line_words[word_index])
            except ValueError:
                print("identifier: ",  line_words[word_index])  
        word_index = word_index + 1


line_index = 0

while line_index < len(input_file_lines):
    if len(input_file_lines[line_index]) == 0:
        line_index = line_index + 1
        continue

    if input_file_lines[line_index][0] == "sow":
        if len(input_file_lines[line_index]) == 4:
            if is_valid_variable_name(input_file_lines[line_index][1]) and (input_file_lines[line_index][2] == "of"):
                print_tokens(input_file_lines[line_index])
            else:
                parse_fail(None)
        elif len(input_file_lines[line_index]) == 5:
            if is_integral(input_file_lines[line_index][1]) and is_valid_variable_name(input_file_lines[line_index][2]) and (input_file_lines[line_index][3] == "of"):
                print_tokens(input_file_lines[line_index])
            else:
                parse_fail(None)
        else:
            parse_fail(None)

    elif input_file_lines[line_index][0][0] == "⚠":
        print("comment: ", ' '.join(input_file_lines[line_index])[1:])

    elif input_file_lines[line_index][1] == "is":
        

        
    else:
        print_tokens(input_file_lines[line_index])
    line_index = line_index + 1