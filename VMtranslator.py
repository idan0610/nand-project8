import sys
import os

arithmetics_table = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
commands_map = {}
commands_map['arithmetics'] = 0
commands_map['push'] = 1
commands_map['pop'] = 2
commands_map['label'] = 3
commands_map['goto'] = 4
commands_map['if'] = 5
commands_map['function'] = 6
commands_map['return'] = 7
commands_map['call'] = 8

"""
a class for the parser - open the vm files and read lines
"""
class Parser:

    def __init__(self, file):
        self.VM_file = open(file, 'r')
        self.lines = self.VM_file.readlines()
        self.line = 0
        self.num_lines = self.lines.__len__()
        self.VM_file.close()

    def hasMoreCommands(self):
        if self.num_lines - self.line > 0:
            return True
        return False

    def advance(self):
        self.current_command = self.lines[self.line].strip()
        self.line += 1

    def commandType(self):
        line = self.current_command
        first_word = line.split(' ', 1)[0]
        if first_word in arithmetics_table:
            return commands_map['arithmetics']
        elif first_word == 'push':
            return commands_map['push']
        elif first_word == 'pop':
            return commands_map['pop']
        elif first_word == 'label':
            return commands_map['label']
        elif first_word == 'goto':
            return commands_map['goto']
        elif first_word == 'if-goto':
            return commands_map['if']
        elif first_word == 'function':
            return commands_map['function']
        elif first_word == 'call':
            return commands_map['call']
        elif first_word == 'return':
            return commands_map['return']

    def arg1(self):
        line = self.current_command
        words = line.split()
        if self.commandType() == commands_map['arithmetics']:
            return words[0]
        else:
            return words[1]

    def arg2(self):
        line = self.current_command
        words = line.split()
        return words[2]


class CodeWriter:

    label_counter = 0
    return_counter = 0
    current_function = ""

    def __init__(self, output):
        self.asm_file = open(output, 'w')

    def writeInit(self):
        self.asm_file.write("@256\n")
        self.asm_file.write("D = A\n")
        self.asm_file.write("@SP\n")
        self.asm_file.write("M = D\n")
        self.writeCall("Sys.init", 0)


    def writeLabel(self,label):
        self.asm_file.write("(" + self.current_function + "$" + label + ")\n")

    def writeGoTo(self, label):
        self.asm_file.write("@" + self.current_function + "$" + label + "\n")
        self.asm_file.write("0 ; JMP\n")

    def writeIfGoTo(self,label):
        self.asm_file.write("@SP\n")
        self.asm_file.write("M = M - 1\n")
        self.asm_file.write("A = M\n")
        self.asm_file.write("D = M\n")
        self.asm_file.write("@" + self.current_function + "$" + label + "\n")
        self.asm_file.write("D ; JNE\n")

    def writeCall(self, functionName, numLocals):
        self.asm_file.write("@FUNC"+str(self.return_counter)+"\n")
        self.asm_file.write("D = A\n")
        self.__print_push()
        self.asm_file.write("@LCL\n")
        self.asm_file.write("D = M\n")
        self.__print_push()
        self.asm_file.write("@ARG\n")
        self.asm_file.write("D = M\n")
        self.__print_push()
        self.asm_file.write("@THIS\n")
        self.asm_file.write("D = M\n")
        self.__print_push()
        self.asm_file.write("@THAT\n")
        self.asm_file.write("D = M\n")
        self.__print_push()
        # ARG = sp - n -5
        self.asm_file.write("@5\n")
        self.asm_file.write("D = A\n")
        self.asm_file.write("@" + str(numLocals) + "\n")
        self.asm_file.write("D = D + A\n")
        self.asm_file.write("@SP\n")
        self.asm_file.write("D = M - D\n")
        self.asm_file.write("@ARG\n")
        self.asm_file.write("M = D\n")
        self.asm_file.write("@SP\n")
        self.asm_file.write("D = M\n")
        self.asm_file.write("@LCL\n")
        self.asm_file.write("M = D\n")
        #self.writeGoTo(functionName)
        self.asm_file.write("@" + functionName + "\n")
        self.asm_file.write("0 ; JMP\n")
        self.asm_file.write("(FUNC" + str(self.return_counter)+")\n")
        self.return_counter += 1

    def writeFunction(self, name, numVar):
        self.current_function = name
        self.asm_file.write("(" + name + ")\n")
        i = 0
        while i < int(numVar):
            self.asm_file.write("D = 0\n")
            self.__print_push()
            i += 1

    def writeReturn(self):
        self.asm_file.write("@LCL\n")
        self.asm_file.write("D = M\n")
        self.asm_file.write("@R13\n")
        self.asm_file.write("M = D\n")
        self.asm_file.write("@5\n")
        self.asm_file.write("A = D - A\n")
        self.asm_file.write("D = M\n")
        self.asm_file.write("@R14\n")
        self.asm_file.write("M = D\n")
        self.asm_file.write("@SP\n")
        self.asm_file.write("M = M - 1\n")
        self.asm_file.write("A = M\n")
        self.asm_file.write("D = M\n")
        self.asm_file.write("@ARG\n")
        self.asm_file.write("A = M\n")
        self.asm_file.write("M = D\n")
        self.asm_file.write("@ARG\n")
        self.asm_file.write("D = M\n")
        self.asm_file.write("@SP\n")
        self.asm_file.write("M = D + 1\n")
        self.asm_file.write("@R13\n")
        self.asm_file.write("M = M -1\n")
        self.asm_file.write("A = M\n")
        self.asm_file.write("D = M\n")
        self.asm_file.write("@THAT\n")
        self.asm_file.write("M = D\n")
        self.asm_file.write("@R13\n")
        self.asm_file.write("M = M -1\n")
        self.asm_file.write("A = M\n")
        self.asm_file.write("D = M\n")
        self.asm_file.write("@THIS\n")
        self.asm_file.write("M = D\n")
        self.asm_file.write("@R13\n")
        self.asm_file.write("M = M -1\n")
        self.asm_file.write("A = M\n")
        self.asm_file.write("D = M\n")
        self.asm_file.write("@ARG\n")
        self.asm_file.write("M = D\n")
        self.asm_file.write("@R13\n")
        self.asm_file.write("M = M -1\n")
        self.asm_file.write("A = M\n")
        self.asm_file.write("D = M\n")
        self.asm_file.write("@LCL\n")
        self.asm_file.write("M = D\n")
        self.asm_file.write("@R14\n")
        self.asm_file.write("A = M\n")
        self.asm_file.write("0; JMP\n")

    def writeArithmetic(self, command):
        if command == 'add':
            self.asm_file.write("@SP\n")
            self.asm_file.write("M = M - 1\n")
            self.asm_file.write("A = M\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M - 1\n")
            self.asm_file.write("M = M + D\n")

        elif command == 'sub':
            self.asm_file.write("@SP\n")
            self.asm_file.write("M = M - 1\n")
            self.asm_file.write("A = M\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M - 1\n")
            self.asm_file.write("M = M - D\n")

        elif command == 'eq':
            self.asm_file.write("@SP\n")
            self.asm_file.write("M = M - 1\n")
            self.asm_file.write("A = M\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M - 1\n")
            self.asm_file.write("D = M - D\n")
            self.asm_file.write("M = -1\n")
            self.asm_file.write("@CONT"+str(self.label_counter) +"\n")
            self.asm_file.write("D; JEQ\n")
            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M -1\n")
            self.asm_file.write("M = 0\n")
            self.asm_file.write("(CONT" + str(self.label_counter) + ")\n")
            self.label_counter += 1

        elif command == 'gt':


            self.asm_file.write("@SP\n")
            self.asm_file.write("M = M - 1\n")
            self.asm_file.write("A = M\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@R14\n")
            self.asm_file.write("M = 0\n")
            self.asm_file.write("@CONT"+str(self.label_counter) +"\n")
            self.asm_file.write("D; JLT\n")
            self.asm_file.write("@R14\n")
            self.asm_file.write("M = -1\n")
            self.asm_file.write("(CONT" + str(self.label_counter) + ")\n")
            self.label_counter += 1

            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M - 1\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@R13\n")
            self.asm_file.write("M = 0\n")
            self.asm_file.write("@CONT"+str(self.label_counter) +"\n")
            self.asm_file.write("D; JLT\n")
            self.asm_file.write("@R13\n")
            self.asm_file.write("M = -1\n")
            self.asm_file.write("(CONT" + str(self.label_counter) + ")\n")
            self.label_counter += 1

            self.asm_file.write("@R13\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@R14\n")
            self.asm_file.write("D = M - D\n")
            self.asm_file.write("@R15\n")
            self.asm_file.write("M = 0\n")
            self.asm_file.write("@CONT"+str(self.label_counter) +"\n")
            self.asm_file.write("D; JEQ\n")
            self.asm_file.write("@R15\n")
            self.asm_file.write("M = -1\n")
            self.asm_file.write("(CONT" + str(self.label_counter) + ")\n")
            self.label_counter += 1

            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M - 1\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M\n")
            self.asm_file.write("D = D - M\n")
            self.asm_file.write("A = A - 1\n")
            self.asm_file.write("M = 0\n")
            self.asm_file.write("@CONT"+str(self.label_counter)+"\n")
            self.asm_file.write("D; JLE\n")
            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M -1\n")
            self.asm_file.write("M = -1\n")
            self.asm_file.write("(CONT" + str(self.label_counter) + ")\n")
            self.label_counter += 1

            self.asm_file.write("@R15\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@CONT"+str(self.label_counter) +"\n")
            self.asm_file.write("D ; JEQ\n")
            self.asm_file.write("@R13\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M - 1\n")
            self.asm_file.write("M = -1\n")
            self.label_counter += 1
            self.asm_file.write("@CONT"+str(self.label_counter) +"\n")
            self.asm_file.write("D; JNE\n")
            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M - 1\n")
            self.asm_file.write("M = 0\n")
            self.asm_file.write("(CONT" + str(self.label_counter) + ")\n")
            self.asm_file.write("(CONT" + str(self.label_counter - 1) + ")\n")
            self.label_counter += 1


        elif command == 'lt':

            self.asm_file.write("@SP\n")
            self.asm_file.write("M = M - 1\n")
            self.asm_file.write("A = M\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@R14\n")
            self.asm_file.write("M = 0\n")
            self.asm_file.write("@CONT"+str(self.label_counter) +"\n")
            self.asm_file.write("D; JLT\n")
            self.asm_file.write("@R14\n")
            self.asm_file.write("M = -1\n")
            self.asm_file.write("(CONT" + str(self.label_counter) + ")\n")
            self.label_counter += 1

            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M - 1\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@R13\n")
            self.asm_file.write("M = 0\n")
            self.asm_file.write("@CONT"+str(self.label_counter) +"\n")
            self.asm_file.write("D; JLT\n")
            self.asm_file.write("@R13\n")
            self.asm_file.write("M = -1\n")
            self.asm_file.write("(CONT" + str(self.label_counter) + ")\n")
            self.label_counter += 1

            self.asm_file.write("@R13\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@R14\n")
            self.asm_file.write("D = M - D\n")
            self.asm_file.write("@R15\n")
            self.asm_file.write("M = 0\n")
            self.asm_file.write("@CONT"+str(self.label_counter) +"\n")
            self.asm_file.write("D; JEQ\n")
            self.asm_file.write("@R15\n")
            self.asm_file.write("M = -1\n")
            self.asm_file.write("(CONT" + str(self.label_counter) + ")\n")
            self.label_counter += 1

            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M - 1\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M\n")
            self.asm_file.write("D = D - M\n")
            self.asm_file.write("A = A - 1\n")
            self.asm_file.write("M = -1\n")
            self.asm_file.write("@CONT"+str(self.label_counter)+"\n")
            self.asm_file.write("D; JLT\n")
            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M -1\n")
            self.asm_file.write("M = 0\n")
            self.asm_file.write("(CONT" + str(self.label_counter) + ")\n")
            self.label_counter += 1

            self.asm_file.write("@R15\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@CONT"+str(self.label_counter) + "\n")
            self.asm_file.write("D ; JEQ\n")
            self.asm_file.write("@R13\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M - 1\n")
            self.asm_file.write("M = 0\n")
            self.label_counter += 1
            self.asm_file.write("@CONT"+str(self.label_counter) + "\n")
            self.asm_file.write("D; JNE\n")
            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M - 1\n")
            self.asm_file.write("M = -1\n")
            self.asm_file.write("(CONT" + str(self.label_counter) + ")\n")
            self.asm_file.write("(CONT" + str(self.label_counter - 1) + ")\n")
            self.label_counter += 1


        elif command == 'neg':
            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M - 1\n")
            self.asm_file.write("M = -M\n")

        elif command == 'and':
            self.asm_file.write("@SP\n")
            self.asm_file.write("M = M - 1\n")
            self.asm_file.write("A = M\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M - 1\n")
            self.asm_file.write("M = M & D\n")

        elif command == 'or':
            self.asm_file.write("@SP\n")
            self.asm_file.write("M = M - 1\n")
            self.asm_file.write("A = M\n")
            self.asm_file.write("D = M\n")
            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M - 1\n")
            self.asm_file.write("M = M | D\n")

        elif command == 'not':
            self.asm_file.write("@SP\n")
            self.asm_file.write("A = M - 1\n")
            self.asm_file.write("M = !M\n")



    def writePushPop(self,command, segment, index, nameFile):
        if command == 'push':
            if segment == "argument":
                self.asm_file.write("@ARG\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@" + index+"\n")
                self.asm_file.write("A = D + A\n")
                self.asm_file.write("D = M\n")
                self.__print_push()

            elif segment == "local":
                self.asm_file.write("@LCL\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@" + index+"\n")
                self.asm_file.write("A = D + A\n")
                self.asm_file.write("D = M\n")
                self.__print_push()

            elif segment == "static":
                self.asm_file.write("@" + nameFile + "." + index + "\n")
                self.asm_file.write("D = M\n")
                self.__print_push()


            elif  segment == "constant":
                self.asm_file.write("@" + index+"\n")
                self.asm_file.write("D = A\n")
                self.__print_push()

            elif  segment == "this":
                self.asm_file.write("@THIS\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@" + index+"\n")
                self.asm_file.write("A = D + A\n")
                self.asm_file.write("D = M\n")
                self.__print_push()

            elif segment == "that":
                self.asm_file.write("@THAT\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@" + index+"\n")
                self.asm_file.write("A = D + A\n")
                self.asm_file.write("D = M\n")
                self.__print_push()

            elif  segment == "pointer":
                self.asm_file.write("@R3\n")
                self.asm_file.write("D = A\n")
                self.asm_file.write("@" + index+"\n")
                self.asm_file.write("A = D + A\n")
                self.asm_file.write("D = M\n")
                self.__print_push()

            elif  segment == "temp":
                self.asm_file.write("@R5\n")
                self.asm_file.write("D = A\n")
                self.asm_file.write("@" + index+"\n")
                self.asm_file.write("A = D + A\n")
                self.asm_file.write("D = M\n")
                self.__print_push()


        if command == 'pop':
            if segment == "argument":
                self.asm_file.write("@SP\n")
                self.asm_file.write("M = M - 1\n")
                self.asm_file.write("A = M\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@R13\n")
                self.asm_file.write("M = D\n")
                self.asm_file.write("@ARG\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@" + index+"\n")
                self.asm_file.write("D = D + A\n")
                self.asm_file.write("@R14\n")
                self.asm_file.write("M = D\n")
                self.asm_file.write("@R13\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@R14\n")
                self.asm_file.write("A = M\n")
                self.asm_file.write("M = D\n")
            elif segment == "local":
                self.asm_file.write("@SP\n")
                self.asm_file.write("M = M - 1\n")
                self.asm_file.write("A = M\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@R13\n")
                self.asm_file.write("M = D\n")
                self.asm_file.write("@LCL\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@" + index+"\n")
                self.asm_file.write("D = D + A\n")
                self.asm_file.write("@R14\n")
                self.asm_file.write("M = D\n")
                self.asm_file.write("@R13\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@R14\n")
                self.asm_file.write("A = M\n")
                self.asm_file.write("M = D\n")
            elif segment == "static":
                self.asm_file.write("@SP\n")
                self.asm_file.write("M = M - 1\n")
                self.asm_file.write("A = M\n")
                self.asm_file.write("D = M\n")

                self.asm_file.write("@" + nameFile + "." + index + "\n")
                self.asm_file.write("M = D\n")

            elif segment == "constant":
                self.asm_file.write("@SP\n")
                self.asm_file.write("A = M - 1\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@" + index+"\n")
                self.asm_file.write("M = D\n")
                self.asm_file.write("@SP\n")
                self.asm_file.write("D = M - 1\n")
                self.asm_file.write("M = D\n")
            elif segment == "this":
                self.asm_file.write("@SP\n")
                self.asm_file.write("M = M - 1\n")
                self.asm_file.write("A = M\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@R13\n")
                self.asm_file.write("M = D\n")
                self.asm_file.write("@THIS\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@" + index+"\n")
                self.asm_file.write("D = D + A\n")
                self.asm_file.write("@R14\n")
                self.asm_file.write("M = D\n")
                self.asm_file.write("@R13\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@R14\n")
                self.asm_file.write("A = M\n")
                self.asm_file.write("M = D\n")
            elif segment == "that":
                self.asm_file.write("@SP\n")
                self.asm_file.write("M = M - 1\n")
                self.asm_file.write("A = M\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@R13\n")
                self.asm_file.write("M = D\n")
                self.asm_file.write("@THAT\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@" + index+"\n")
                self.asm_file.write("D = D + A\n")
                self.asm_file.write("@R14\n")
                self.asm_file.write("M = D\n")
                self.asm_file.write("@R13\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@R14\n")
                self.asm_file.write("A = M\n")
                self.asm_file.write("M = D\n")
            elif segment == "pointer":
                self.asm_file.write("@SP\n")
                self.asm_file.write("M = M - 1\n")
                self.asm_file.write("A = M\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@R13\n")
                self.asm_file.write("M = D\n")
                self.asm_file.write("@THIS\n")
                self.asm_file.write("D = A\n")
                self.asm_file.write("@" + index+"\n")
                self.asm_file.write("D = D + A\n")
                self.asm_file.write("@R14\n")
                self.asm_file.write("M = D\n")
                self.asm_file.write("@R13\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@R14\n")
                self.asm_file.write("A = M\n")
                self.asm_file.write("M = D\n")
            elif segment == "temp" :
                self.asm_file.write("@SP\n")
                self.asm_file.write("M = M - 1\n")
                self.asm_file.write("A = M\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@R13\n")
                self.asm_file.write("M = D\n")
                self.asm_file.write("@R5\n")
                self.asm_file.write("D = A\n")
                self.asm_file.write("@" + index+"\n")
                self.asm_file.write("D = D + A\n")
                self.asm_file.write("@R14\n")
                self.asm_file.write("M = D\n")
                self.asm_file.write("@R13\n")
                self.asm_file.write("D = M\n")
                self.asm_file.write("@R14\n")
                self.asm_file.write("A = M\n")
                self.asm_file.write("M = D\n")



    def __print_push(self):
        self.asm_file.write("@SP\n")
        self.asm_file.write("A = M\n")
        self.asm_file.write("M = D\n")
        self.asm_file.write("@SP\n")
        self.asm_file.write("M = M + 1\n")

    def Close(self):
        self.asm_file.close()


def main(args):
    if os.path.isdir(args):
        path = os.path.normpath(args)
        path_list = path.split(os.sep)
        name_writer = path_list[-1]
        if not args.endswith('/'):
            args = args + '/'
        writer = CodeWriter(args + name_writer + '.asm')
        writer.writeInit()
        for filename in os.listdir(args):
            if filename.endswith('.vm'):
                input_name = filename.rsplit('.', 1)[0]
                name_file = args + filename
                parser = Parser(name_file)
                while parser.hasMoreCommands():
                    parser.advance()
                    if parser.current_command == '\n' or parser.current_command.startswith('//'):
                        continue
                    if parser.commandType() == commands_map['arithmetics']:
                        writer.writeArithmetic(parser.arg1())
                    elif parser.commandType() == commands_map['push']:
                        writer.writePushPop('push', parser.arg1(), parser.arg2(),input_name)
                    elif parser.commandType() == commands_map['pop']:
                        writer.writePushPop('pop', parser.arg1(), parser.arg2(), input_name)
                    elif parser.commandType() == commands_map['label']:
                        writer.writeLabel(parser.arg1())
                    elif parser.commandType() == commands_map['goto']:
                        writer.writeGoTo(parser.arg1())
                    elif parser.commandType() == commands_map['if']:
                        writer.writeIfGoTo(parser.arg1())
                    elif parser.commandType() == commands_map['function']:
                        writer.writeFunction(parser.arg1(), parser.arg2())
                    elif parser.commandType() == commands_map['call']:
                        writer.writeCall(parser.arg1(), parser.arg2())
                    elif parser.commandType() == commands_map['return']:
                        writer.writeReturn()

    elif os.path.isfile(args):
        if args.endswith('.vm'):
            name_writer = args.rsplit('.', 1)[0]
            input_name = name_writer
            name_writer = name_writer + ".asm"
            writer = CodeWriter(name_writer)
            writer.writeInit()
            parser = Parser(args)
            while parser.hasMoreCommands():
                    parser.advance()
                    if parser.current_command == '\n' or parser.current_command.startswith('//'):
                        continue
                    if parser.commandType() == commands_map['arithmetics']:
                        writer.writeArithmetic(parser.arg1())
                    elif parser.commandType() == commands_map['push']:
                        writer.writePushPop('push', parser.arg1(), parser.arg2(),input_name)
                    elif parser.commandType() == commands_map['pop']:
                        writer.writePushPop('pop', parser.arg1(), parser.arg2(),input_name)
                    elif parser.commandType() == commands_map['label']:
                        writer.writeLabel(parser.arg1())
                    elif parser.commandType() == commands_map['goto']:
                        writer.writeGoTo(parser.arg1())
                    elif parser.commandType() == commands_map['if']:
                        writer.writeIfGoTo(parser.arg1())
                    elif parser.commandType() == commands_map['function']:
                        writer.writeFunction(parser.arg1(), parser.arg2())
                    elif parser.commandType() == commands_map['call']:
                        writer.writeCall(parser.arg1(), parser.arg2())
                    elif parser.commandType() == commands_map['return']:
                        writer.writeReturn()

    else:
        print("error: file or folders does not exist")

main(sys.argv[1])