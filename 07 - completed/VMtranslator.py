#https://docs.python.org/3/howto/argparse.html

import sys
import re
import os

class tokens():
    #define regular expression patterns
    space = r"[ \t]+"
    def __init__(self):
        self.memory = r"(?P<memory>(push)|(pop))"
        self.segment = r"(?P<segment>(argument)|(local)|(static)|(this)|(that)|(pointer)|(temp))"
        self.segmentNum = r"(?P<segmentNum>(\d+))"
        self.pushpop = r"(?P<pushpop>" + self.memory + tokens.space + self.segment + tokens.space + self.segmentNum + r")"
        self.constant = r"(push" + tokens.space + r"constant" + tokens.space + r"(?P<constant>(\d+)))"
        self.memoryaccess = r"(?P<memoryaccess>" +  self.pushpop + r"|" + self.constant + r")"

        self.arithmetic = r"(?P<arithmetic>(add)|(sub)|(neg)|(eq)|(gt)|(lt)|(and)|(or)|(not))"

        self.comment = r"(?P<comment>//.*$)"

        self.label = r"(label" + tokens.space + r"(?P<label>[a-zA-Z]+))"

        self.goto = r"(goto" + tokens.space +  r"(?P<goto>[a-zA-Z]+))"
        self.ifgoto = r"(" + re.escape(r"if-goto") + tokens.space + r"(?P<ifgoto>[a-zA-Z]+))"
        self.goflow = r"(?P<goflow>" + self.goto + r"|" + self.ifgoto  + r")"

        self.funcNum = r"(?P<funcNum>(\d+))"
        self.function = r"(function" + tokens.space + r"(?P<function>[a-zA-Z]+)" + tokens.space + self.funcNum + r")"

        self.call = r"(call" + tokens.space + r"(?P<call>[a-zA-Z]+))" #don't know how functions are called yet

        self.funcReturn = r"(?P<funcReturn>return)"
        self.funcFlow = r"(?P<funcFlow>" + self.label + "|" + self.goflow + "|" + self.function + "|" + self.call + "|" + self.funcReturn + ")"

        self.line = r"(?P<line>" + self.memoryaccess + "|" + self.arithmetic + "|" + self.funcFlow + ")"


class parser():
    def __init__(self, fname):
        extens = os.path.basename(fname).rsplit(".", 1)[1]
        self.oname = fname[:-len(extens)-1] + ".asm"
        self.tokens = tokens()
        regEx = re.compile(self.tokens.comment)
        self.labelDict = dict()
        #open the file, remove all whitespace and comments, return as a list
        with open(fname, 'r') as file:
            #generator comprehension inside a list comprehension -
            #   remove all comments and whitespaces from each line in the input file
            #   add all items which still exist to the list
            self.lns = [j for j in (regEx.sub("",i.strip()) for i in file) if j]
            regEx = re.compile(self.tokens.label)
            i = 0
            #wait until chapter 8 to implement labels
            while False: # i < len(self.lns):
                match = regEx.match(self.lns[i])
                if match:
                    l = match.group("label")
                    self.labelDict[l] = i
                    self.lns.pop(i)
                    i -= 1
                i += 1
            #self.nextSymbol = self.tokens.nextSymbol

    def parse(self):
        regEx = re.compile(self.tokens.line, re.IGNORECASE)
        if os.path.isfile(self.oname):
            os.remove(self.oname)

        with open(self.oname, "a") as o:
            for i in self.lns:
                out = ""
                match = regEx.match(i)
                if not match:
                    raise Exception("Invalid line: \n" + i + "\n" + ";".join(str(ord(j)) for j in i) + "\n" + regEx.pattern)
                if match.group("memoryaccess"):
                    if match.group("pushpop"):
                        n = match.group("segmentNum")
                        s = parser.segmentDict[match.group("segment")].format(n)
                        p = parser.pushpopDict[match.group("memory")]
                        out = s + "\n" + p
                    elif match.group("constant"):
                        out = parser.pushconst.format(match.group("constant"))
                    else:
                        raise Exception("Invalid line: \n" + i + "\n"  + regEx.pattern)
                elif match.group("arithmetic"):
                    arfun = match.group("arithmetic")
                    arnum  = parser.arithNs[arfun]
                    out = parser.arithmeticDict[arfun].format(arnum)
                    parser.arithNs[arfun] += 1
                    #the string formatting is only required for eq, gt, lt, but I am doing it for all of the functions to
                    #simplify the code
                elif match.group("funcFlow"):
                    raise Exception("function flow not yet validated: \n" + i + "\n" + ";".join(str(ord(j)) for j in i) + "\n" + regEx.pattern)
                else:
                    raise Exception("Invalid line: \n" + i + "\n"  + regEx.pattern)
                o.write(out + "\n")

    """
    The following is a lookup dictionary of the form <arithmetic VM function>:<hack assembly code>.
    The boolean functions have goto statements using labels.  In order to avoid duplication of the labels, call the
    string.format(n) function to append n to each of the labels, where 'n' is the number of times that boolean
    function has been called so far in the .asm file.
    """
    arithmeticDict = {
        "add":"""@SP //add
    M=M-1 //leave stack+2 as-is
    A=M
    D=M  //D = y
    @SP
    M=M-1 //leave stack+1 as-is
    A=M
    D=D+M  //D = y + x
    @SP
    A=M
    M=D //done add
    @SP
    M=M+1 //increment stack""",

        "sub":"""@SP //subtract
    M=M-1 //leave stack+2 as-is
    A=M
    D=-M  //D = -y
    @SP
    M=M-1 //leave stack+1 as-is
    A=M
    D=D+M //D = -y + x
    @SP
    A=M
    M=D //done subtract
    @SP
    M=M+1 //increment stack""",

        "neg":"""@SP //negative
    M=M-1 //leave stack+1 as-is
    A=M
    M=-M //done negative
    @SP
    M=M+1 //increment stack""",

        "eq":"""@SP //test equality
    M=M-1 //leave stack+2 as-is
    A=M
    D=-M //D = -y
    @SP
    M=M-1 //leave stack+1 as-is
    A=M
    D=D+M //D = -y + x
    @EQUAL{0}
    D;JEQ //if D = 0, jump
    @SP
    A=M
    M=0 //false indicated by 0
    @DONETESTEQUALITY{0}
    0;JMP
    (EQUAL{0})
    @SP
    A=M
    M=-1 //true indicated by -1
    (DONETESTEQUALITY{0}) //done test equality
    @SP
    M=M+1 //increment stack""",

        "gt":"""@SP //test greater than
    M=M-1 //leave stack+2 as-is
    A=M
    D=-M //D = -y
    @SP
    M=M-1 //leave stack+1 as-is
    A=M
    D=D+M //D = -y + x
    @GREATERTHAN{0}
    D;JGT //if D > 0, jump
    @SP
    A=M
    M=0 //false indicated by 0
    @DONEGREATERTHAN{0}
    0;JMP
    (GREATERTHAN{0})
    @SP
    A=M
    M=-1 //true indicated by -1
    (DONEGREATERTHAN{0}) //done test greater than
    @SP
    M=M+1 //increment stack""",

        "lt":"""@SP //test less than
    M=M-1 //leave stack+2 as-is
    A=M
    D=-M //D = -y
    @SP
    M=M-1 //leave stack+1 as-is
    A=M
    D=D+M //D = -y + x
    @LESSTHAN{0}
    D;JLT //if D < 0, jump
    @SP
    A=M
    M=0 //false indicated by 0
    @DONELESSTHAN{0}
    0;JMP
    (LESSTHAN{0})
    @SP
    A=M
    M=-1 //true indicated by -1
    (DONELESSTHAN{0}) //done test less than
    @SP
    M=M+1 //increment stack""",

        "and":"""@SP //bitwise and
    M=M-1 //leave stack+2 as-is
    A=M
    D=M
    @SP
    M=M-1 //leave stack+1 as-is
    A=M
    D=D&M
    @SP
    A=M
    M=D //done bitwise and
    @SP
    M=M+1 //increment stack""",

        "or":"""@SP //bitwise or
    M=M-1 //leave stack+2 as-is
    A=M
    D=M
    @SP
    M=M-1 //leave stack+1 as-is
    A=M
    D=D|M
    @SP
    A=M
    M=D //done bitwise or
    @SP
    M=M+1 //increment stack""",

        "not":"""@SP //bitwise not
    M=M-1 //leave stack+1 as-is
    A=M
    M=!M //done bitwise not
    @SP
    M=M+1 //increment stack"""
    }

    arithNs = {i:0 for i in arithmeticDict.keys()}
    # use this dictionary to count the number of times a given function has been called.
    # this is only necessary for the lt gt eq functions, but I'm doing this for all functions for now.

    """
    push sends the value in R13 to the top of the stack and then increments the stack by one
    """
    push = """@R13 //push: sends the value in R13 to the top of the stack and then increments the stack by one
    A=M
    D=M  //D now holds value from sector in R13
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //increment the stack; done push"""
    #to use pushconst, call string.format(const)
    pushconst = """@{0} //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack"""

    """
    pop decrements the stack and then sends the top value in the stack to sector pointed to in R13
    """
    pop = """@SP //pop:  decrements the stack and then sends the top value in the stack to sector pointed to in R13
    M=M-1  //decrement stack pointer
    @SP
    A=M
    D=M //D now holds top stack value
    @R13
    A=M
    M=D //done pop: sector from R13 now holds the value"""
    pushpopDict = {"push":push, "pop":pop}

    """
    The following is a lookup dictionary of the form <segmentName>:<hack assembly code>.
    This code sets R13 to the address pointed to by <segmentName>.  The dictionary values assume
    that a segment index will be set.  To call the code properly, use string.format(i), where
    i is the segment index.
    the <this> and <that> sectors do not need to be formatted as such, and should only allow
    segment index 0, as they are length-1 sectors.
    """
    segmentDict = {
        "argument":"""@ARG //argument: set R13 to <argument> sector in memory (index ??)
    D=M
    @{0}
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector""",
        "local":"""@LCL //local: set R13 to <local> sector in memory (index ??)
    D=M
    @{0}
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector""",
        "static":"""@ARG //static: set R13 to <static> sector in memory (index ??)
    D=M
    @{0}
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector""",
        "this":"""@THIS //this: set R13 to <this> sector in memory (index ??)
    D=M
    @{0}
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector""",
        "that":"""@THAT //that: set R13 to <that> sector in memory (index ??)
    D=M
    @{0}
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector""",
        "pointer":"""@THIS //pointer: set R13 to <pointer> sector in memory (index 0 to 1)
    D=A
    @{0}
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector""",
        "temp":"""@R5 //pointer: set R13 to <temp> sector in memory (index 0 to 7)
    D=A
    @{0}
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector"""
    }


def main():
    #parser = parse_args(sys.argv[1:])
    fname = sys.argv[1]

    p = parser(fname)
    p.parse()

if __name__ == '__main__':
    main()