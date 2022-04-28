# for accessing command-line arguments passed to the script.
import sys
# for regular expressions
import re

# operators in the SPADE language, no identifier can contain these characters. This also includes superscript numbers, as we shall see in our regex
spade_operators = [ "+", "-", "×", "÷", "/", "&", "|", "^", "√", "=", "!", "~", "#", ">", "<", "[", "]", "←", "→", "≥", "≤", "≠", "%", ",", "&&", "||"]

# keywords in the SPADE language, no identifier can be named these.
spade_keywords = [ "sow", "with", "reap", "plant", "of", "here", "lies", "is", "harvest", "from", "until", "eternally", "every", "⏵", "sell", "⚠", "fresh?", "rotten", "dispose", "kill", "skip", "supply", "unearth", "bury", "engrave", "on", "stdout", "stderr", "i64", "u64", "f64", "i32", "u32", "f32", "b8", "b1", "c32", "c∞", "file", "❌", "⭕", "__________", "|__________", "|", "(", ")"]

# SPADE uses superscript for constant exponents, to parse and convert them to integer constants these are needed.
# To handle superscript, we consider the superscript digits as operators and parse them as an expression.
superscript_numbers = ["⁰","¹","²","³","⁴","⁵","⁶","⁷","⁸","⁹"]
superscript_map = {"⁰":"0","¹":"1","²":"2","³":"3","⁴":"4","⁵":"5","⁶":"6","⁷":"7","⁸":"8","⁹":"9"}

tokens = []
#parse fail case
def parse_fail(error: str, line_index: int):
    print(error)
    print("Parsing failed at line #", line_index)
    exit(1)

# prints the token number as a hex
def print_hex(token_id: int):
    return str.format("0x{:02x}", token_id)

# convert a superscript integer constant to normal integers for printing as a token. 
# Normal integer constants are also passed to this, but are left unchanged.
def desuperscriptify(word: str):
    word_list  = []
    for char in word:
        word_list.append(superscript_map.get(char, char))
    return ''.join(word_list)

# prints a new token along with metadata, if token is parsed as an expression, it is "split" and then passed to print_token recursively.
def print_token(word: str, line_index: int):
    if is_integer_constant(word,line_index):
        # print(('\t' * 4).join([str(line_index + 1), print_hex(129), "INT_CONSTANT", desuperscriptify(word)]))
        tokens.append((line_index + 1, "INT_CONSTANT", desuperscriptify(word)))
    elif is_float_constant(word):
        # print(('\t' * 4).join([str(line_index + 1), print_hex(130), "FP_CONSTANT", word]))
        tokens.append((line_index + 1, "FP_CONSTANT", word))
    elif is_keyword(word):
        # print(('\t' * 4).join([str(line_index + 1), print_hex(spade_keywords.index(word)), "SPADE_KEYWORD", word]))
        tokens.append((line_index + 1, "SPADE_KEYWORD", word))
    elif is_valid_variable_name(word):
        # print(('\t' * 4).join([str(line_index + 1), print_hex(128), "IDENTIFIER", word]))
        tokens.append((line_index + 1, "IDENTIFIER", word))
    elif is_operator(word):
        # print(('\t' * 4).join([str(line_index + 1), print_hex(64 + spade_operators.index(word)), "SPADE_OPERATOR", word]))
        tokens.append((line_index + 1, "SPADE_OPERATOR", word))
    else:
        split_word = is_expr(word)
        for word in split_word:
            print_token(word, line_index)

def is_integer_constant(word: str, line_index: int):
    try:
        # uses Python's internal int() function to parse integer constants. Can handle hexadecimal, octal and binary numbers as well.
        int(word, base = 0)
    except ValueError:
        if len([superscript for superscript in list(word) if superscript in superscript_numbers]) == len(list(word)):
            # print(('\t' * 4).join([str(line_index + 1), print_hex(64 + spade_operators.index('^')), "SPADE_OPERATOR", '^']))
            tokens.append((line_index + 1, "SPADE_OPERATOR", '^'))
            return True
        return False
    return True

def is_float_constant(word: str):
    try:
        # uses Python's internal float() function to parse floating-point constants.
        float(word)
    except ValueError:
        return False
    return True

def is_keyword(word: str):
    if word in spade_keywords:
        return True
    return False

def is_valid_variable_name(word: str):
    # has additional clause to check superscript numbers
    if len([ character for character in list(word) if character in (spade_keywords + spade_operators + superscript_numbers) ]) > 0:
        return False
    return True

def is_operator(word: str):
    if word in spade_operators:
        return True
    return False

def is_expr(word: str):
    #Insane regex string to split expressions by operators and superscript numbers while still capturing those characters in the list
    split_word = list(filter(None, re.split("([\u2070\u00b9\u00b2\u00b3\u2074-\u2079]+)|(≤)|(≥)|(>)|(<)|(&&)|(\|\|)|(\+)|(-)|(×)|(÷)|(\/)|(&)|(\|)|(\^)|(√)|(\=)|(%)|(≠)|(\!)|(~)|(#)|(←)|(→)|(\[)|(\])|(\()|(\))|(,)", word)))
    return split_word

def tokenize(filename):
    
    # opening a file from command line, splitting it by newlines and then splitting by whitespace.
    input_file_lines = list(map(lambda line: list(filter(None, re.split("\n|([ \t]+)", line))), open(filename, "r", encoding = 'utf8').readlines()))

    # print("\n\nLINE_NUMBER\t\t\tTOKEN_ID\t\t\tTOKEN_TYPE\t\t\t\tTOKEN CONTENTS")

    # looping over each line.
    for line_index, line in enumerate(input_file_lines):
        # handling struct enclosures as well as empty lines and comments.
        if len(line) == 0 or line[0][0] == "⚠":
            continue
        # while in a struct enclosure, the first | is part of the enclosure and not an operator.
        elif line[0] == "|":
            # print(('\t' * 4).join([str(line_index + 1), print_hex(spade_keywords.index('|')), "SPADE_KEYWORD", '|']))
            tokens.append((line_index + 1, "SPADE_KEYWORD", '|'))
            line = line[1:]
        
        word_index = 0
        while word_index < len(line):
            # whitespace is only tracked when we need to print string constants, otherwise we just ignore it.
            if ' ' in line[word_index]:
                word_index = word_index + 1
                continue
            # last character of a variable cannot be a " if first character isn't a "
            elif len(line[word_index]) > 1 and line[word_index][-1] == "\"" and line[word_index][0] != "\"":
                parse_fail("Error parsing, (\") is an illegal character.\nLine: " + ''.join(line), line_index + 1)
            # handling string constants. we also have escape sequences as part of string constants, so parsing is slightly complex.
            elif line[word_index][0] == "\"":
                if line[word_index][-1] == "\"" and len(line[word_index]) > 1 and line[word_index][-2] != "\\":
                    string_constant = line[word_index]
                else:
                    string_constant = line[word_index]
                    word_index = word_index + 1
                    #We need to ensure that \" is not considered while analysis since it has been escaped
                    while word_index < len(line) and (line[word_index][-1] != "\"" or (len(line[word_index]) > 1 and line[word_index][-2] == "\\")):
                        string_constant = string_constant + line[word_index]
                        word_index = word_index + 1
                    if word_index == len(line):
                        print(string_constant, len(string_constant))
                        parse_fail("Error parsing, string constant is unterminated.\nLine: " + ''.join(line), line_index + 1)
                    string_constant = string_constant + line[word_index]
                    #Does the string only contain one " ?
                    if string_constant.count("\"") == 1:
                        print(string_constant, len(string_constant))
                        parse_fail("Error parsing, string constant is unterminated.\nLine: " + ''.join(line), line_index + 1)      
                # print(('\t'*4).join([ str(line_index + 1), print_hex(131), "STRING_CONSTANT", string_constant.strip()[1:-1] ]))
                tokens.append((line_index + 1, "STRING_CONSTANT", string_constant.strip()[1:-1]))
                word_index = word_index + 1
            else:
                # if it's skipped or handled as a string constant, it's handled by print_token.
                print_token(line[word_index], line_index)
            word_index = word_index + 1

        # print(('\t'*4).join([str(line_index + 1), print_hex(132), "NEW_LINE", "\\n"]))
        tokens.append((line_index + 1, "NEW_LINE", "\\n"))

    return tokens