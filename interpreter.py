"""
Author: rdbende
License: GNU GPLv3
Copyright: 2021 rdbende
"""

import sys

stop = False
running = False
exit = sys.exit

def execute(file):
    global stop
    global running
    stop = False
    running = True
    with open(file) as program:
        program_content = program.read()
        
    position = 0
    pointer = 0
    memory = [0]

    bracemap = build_bracemap(program_content)
    
    while position < len(program_content):
        if program_content[position] == ">":
            pointer += 1
            if len(memory) <= pointer:
                memory.append(0)
                
        elif program_content[position] == "<":
            pointer -= 1
            if pointer < 0:
                print("Range error")
                exit()

        elif program_content[position] == "+":
            memory[pointer] += 1
            if memory[pointer] > 255:
                memory[pointer] = 0
                
        elif program_content[position] == "-":
            memory[pointer] -= 1
            if memory[pointer] < 0:
                memory[pointer] = 255
                
        elif program_content[position] == ".":
            print(chr(memory[pointer]), end="")
            
        elif program_content[position] == ",":
            memory[pointer] = ord(input()[0])

        elif program_content[position] == "[" and memory[pointer] == 0:
            try:
                position = bracemap[position]
            except KeyError:
                print("Key Error")
                exit()
            
        elif program_content[position] == "]" and memory[pointer] != 0:
            try:
                position = bracemap[position]
            except KeyError:
                print("Key Error")
                exit()
                
        if stop:
            running = False
            exit()
        
        position += 1
    running = False
    exit()


def build_bracemap(code):
    """
    The pre-parse of the braces can speed up interpretation terribly
    Credits for this function: github.com/pocmo/Python-Brainfuck
    """
    temp, bracemap = [], {}

    try:
        for position, command in enumerate(code):
            if command == "[": temp.append(position)
            if command == "]":
                start = temp.pop()
                bracemap[start] = position
                bracemap[position] = start
        return bracemap
    except IndexError:
        print("Parse Error")
        exit()
