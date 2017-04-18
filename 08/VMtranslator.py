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
        self.memoryaccess = r"(?P<memoryaccess>" + self.pushpop + r"|" + self.constant + r")"

        self.arithmetic = r"(?P<arithmetic>(add)|(sub)|(neg)|(eq)|(gt)|(lt)|(and)|(or)|(not))"

        self.comment = r"(?P<comment>//.*$)"

        self.label = r"(?P<label>[a-zA-Z_.$:][\w_.$:]*)"
        self.flowType = r"(?P<flowType>(label)|(goto)|(" + re.escape(r"if-goto") + "))"
        self.labelFlow = r"(?P<labelFlow>" + self.flowType + tokens.space + self.label + r")"

        self.CallFunction = r"(?P<CallFunction>(call)|(function))"
        self.function = r"(?P<function>[a-zA-Z_.:][\w_.:]*)"
        self.funcNum = r"(?P<funcNum>(\d+))"
        self.funcFlow = r"(?P<funcFlow>" + self.CallFunction + tokens.space + self.function + tokens.space + self.funcNum + ")"

        self.funcReturn = r"(?P<funcReturn>return)"

        self.flow = r"(?P<flow>" + self.labelFlow + "|" + self.funcFlow + "|" + self.funcReturn + ")"

        self.line = r"^(?P<line>" + self.memoryaccess + "|" + self.arithmetic + "|" + self.flow + ")$"


class parser():
    def __init__(self, folder):
        abspath = os.path.abspath(folder)
        self.oname = (os.path.join(folder, os.path.basename(abspath) + ".asm"))
        addStatic = 0
        self.tokens = tokens()
        staticRegEx = re.compile(self.tokens.pushpop)
        sysVM = os.path.join(folder, "sys.vm")
        if os.path.exists(sysVM):
            self.bootstrap = True
        else:
            self.bootstrap = False
        self.lns = []
        for fname in os.listdir(folder):
            if fname[-3:] == ".vm":
                maxStatic = addStatic
                regEx = re.compile(self.tokens.comment)
                self.labelDict = dict()
                self.callDict = dict()
                # open the file, remove all whitespace and comments, return as a list
                with open(os.path.join(folder, fname), 'r') as file:
                    # generator comprehension inside a list comprehension -
                    #   remove all comments and whitespaces from each line in the input file
                    #   add all items which still exist to the list
                    tmp = [j for j in (regEx.sub("", i).strip() for i in file) if j]
                    for (index, line) in enumerate(tmp): #fix static variables
                        s = staticRegEx.search(line)
                        if s:
                            if s.group("segment") == "static":
                                n = s.group("segmentNum")
                                intN = int(n) + addStatic
                                if intN > maxStatic:
                                    maxStatic = intN
                                newline = tmp[index][:-len(n)] + str(intN)
                                tmp[index] = newline
                addStatic = maxStatic + 1
                self.lns += tmp

    def parse(self):
        regEx = re.compile(self.tokens.line, re.IGNORECASE)
        if os.path.isfile(self.oname):
            os.remove(self.oname)
        with open(self.oname, "a") as o:
            if self.bootstrap:
                # bootstrap code:  initialize stack pointer, local, arg to 256, this, that to 2048, call Sys.Init
                o.write("""@256
D=A
@SP
M=D
@LCL
M=D
@ARG
M=D
@2048
D=A
@THIS
M=D
@THAT
M=D
@Sys.init //goto Sys.init
0;JMP
""")
            for i in self.lns:
                out = ""
                match = regEx.match(i)
                if not match:
                    raise Exception("Invalid line: \n" + i + "\n" + regEx.pattern)
                if match.group("memoryaccess"):
                    if match.group("pushpop"):
                        n = match.group("segmentNum")
                        s = parser.segmentDict[match.group("segment")].format(n)
                        p = parser.pushpopDict[match.group("memory")]
                        out = s + p
                    elif match.group("constant"):
                        out = parser.pushconst.format(match.group("constant"))
                    else:
                        raise Exception("Invalid line: \n" + i + "\n" + regEx.pattern)
                elif match.group("arithmetic"):
                    arfun = match.group("arithmetic")
                    arnum = parser.arithNs[arfun]
                    out = parser.arithmeticDict[arfun].format(arnum)
                    parser.arithNs[arfun] += 1
                    # the string formatting is only required for eq, gt, lt, but I am doing it for all of the functions
                    # to simplify the code
                elif match.group("flow"):
                    if match.group("labelFlow"):
                        out = parser.flowDict[match.group("flowType")].format(match.group("label"))
                    elif match.group("funcFlow"):
                        f = match.group("function")
                        #currentFunc = f
                        fnum = match.group("funcNum")
                        ftyp = match.group("CallFunction")
                        if ftyp == "function":
                            out = parser.function(f, fnum)
                        elif ftyp == "call":
                            if f in self.callDict.keys():
                                self.callDict[f] += 1
                            else:
                                self.callDict[f] = 0
                            out = parser.call(f, fnum, self.callDict[f])
                        else:
                            raise Exception("Invalid line: \n" + i + "\n" + regEx.pattern)
                    elif match.group("funcReturn"):
                        out = parser.fReturn()
                    else:
                        raise Exception("Invalid line: \n" + i + "\n" + regEx.pattern)
                else:
                    raise Exception("Invalid line: \n" + i + "\n" + regEx.pattern)
                o.write(out)

    """
    The following is a lookup dictionary of the form <arithmetic VM function>:<hack assembly code>.
    The boolean functions have goto statements using labels.  In order to avoid duplication of the labels, call the
    string.format(n) function to append n to each of the labels, where 'n' is the number of times that boolean
    function has been called so far in the .asm file.
    """
    arithmeticDict = {
        "add": """@SP //add
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
    M=M+1 //increment stack
""",

        "sub": """@SP //subtract
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
    M=M+1 //increment stack
""",

        "neg": """@SP //negative
    M=M-1 //leave stack+1 as-is
    A=M
    M=-M //done negative
    @SP
    M=M+1 //increment stack
""",

        "eq": """@SP //test equality
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
    M=M+1 //increment stack
""",

        "gt": """@SP //test greater than
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
    M=M+1 //increment stack
""",

        "lt": """@SP //test less than
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
    M=M+1 //increment stack
""",

        "and": """@SP //bitwise and
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
    M=M+1 //increment stack
""",

        "or": """@SP //bitwise or
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
    M=M+1 //increment stack
""",

        "not": """@SP //bitwise not
    M=M-1 //leave stack+1 as-is
    A=M
    M=!M //done bitwise not
    @SP
    M=M+1 //increment stack
"""
    }

    arithNs = {i: 0 for i in arithmeticDict.keys()}
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
    M=M+1 //increment the stack; done push
"""
    # to use pushconst, call string.format(const)
    pushconst = """@{0} //push const {0}: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
"""

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
    M=D //done pop: sector from R13 now holds the value
"""

    pushpopDict = {"push": push, "pop": pop}

    """
    The following is a lookup dictionary of the form <segmentName>:<hack assembly code>.
    This code sets R13 to the address pointed to by <segmentName>.  The dictionary values assume
    that a segment index will be set.  To call the code properly, use string.format(i), where
    i is the segment index.
"""
    segmentDict = {
        "argument": """@ARG //argument: set R13 to <argument> sector in memory (index {0})
    D=M
    @{0}
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector
""",
        "local": """@LCL //local: set R13 to <local> sector in memory (index {0})
    D=M
    @{0}
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector
""",
        "static": """@16 //static: set R13 to <static> sector in memory (index {0})
    D=M
    @{0}
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector
""",
        "this": """@THIS //this: set R13 to <this> sector in memory (index {0})
    D=M
    @{0}
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector
""",
        "that": """@THAT //that: set R13 to <that> sector in memory (index {0})
    D=M
    @{0}
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector
""",
        "pointer": """@THIS //pointer: set R13 to <pointer> sector in memory (index {0})
    D=A
    @{0}
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector
""",
        "temp": """@R5 //temp: set R13 to <temp> sector in memory (index {0})
    D=A
    @{0}
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector
""",
        "stackpointer": """@SP //stackpointer: set R13 to <SP>
    D=M
    @R13
    M=D //R13 now holds memory value of correct sector
""",
        "*stackpointer": """@R13 //stackpointer: set R13 to <SP> sector in memory
    M=0 //R13 now holds memory value of correct sector
""",
        "*argument": """@ARG //argument: set R13 to <ARG>
    D=A
    @R13
    M=D //R13 now holds memory value of correct sector
""",
        "*local": """@LCL //local: set R13 to <LCL>
    D=A
    @R13
    M=D //R13 now holds memory value of correct sector
""",
        "*static": """@16 //static: set R13 to <static>
    D=M
    @R13
    M=D //R13 now holds memory value of correct sector
""",
        "*this": """@THIS //this: set R13 to <this>
    D=M
    @R13
    M=D //R13 now holds memory value of correct sector
""",
        "*that": """@THAT //that: set R13 to <that>
    D=M
    @R13
    M=D //R13 now holds memory value of correct sector
"""}

    """
    The following is a lookup dictionary of the form <flow statement>:<hack assembly code>.
    The items in this dictionary expect to have a unique .asm-valid label.  To use the items in this
    dictionary, call string.format(labelname)
    """
    flowDict = {"label": "({0})\n",
                "goto": """@{0}//goto
    0;JMP //done goto
""",
                "if-goto": "//if-goto\n" + segmentDict["temp"].format("0") + pop + """
    @R5
    D=M
    @{0}
    D;JNE //done if-goto
"""}
    # firstline = pushconst.format("{0}.return.{2}")
    # #add comments
    # firstline = firstline.split("\n", 1)[0].split(r"//")[0] + "//call {0} {1}; save state \n" + \
    #             firstline.split("\n", 1)[1]
    # #pushconst.format("{0}.return.{2}").replace("\n", "//call {0} {1}; save state \n", 1) +
    # callstring = (firstline +
    #               segmentDict["*local"] + push +
    #               segmentDict["*argument"] + push +
    #               segmentDict["*this"] + push +
    #               segmentDict["*that"] + "//state saved \n".join(push.rsplit("\n", 1)) +
    #               segmentDict["*stackpointer"].replace("\n", "//set arg pointer \n", 1) + push +
    #               pushconst.format("{1}") +
    #               arithmeticDict["sub"] +
    #               pushconst.format("5") +
    #               arithmeticDict["sub"] +
    #               segmentDict["*argument"] + "//arg pointer set \n".join(pop.rsplit("\n", 1)) +
    #               segmentDict["stackpointer"].replace("\n", "//set local pointer \n", 1) + push +
    #               segmentDict["*local"] + "//local pointer set \n".join(pop.rsplit("\n", 1)) +
    #               flowDict["goto"].format("{0}").replace("\n", "//go to function {0} \n", 1) +
    #               "//done call \n".join(
    #                   flowDict["label"].format("{0}.return.{2}").replace("\n", "//return label \n", 1).rsplit("\n", 1)))

    @classmethod
    def call(cls, functionName, numArgs, callNum):
        #return cls.callstring.format(functionName, numArgs, callNum)
        n = 5 + int(numArgs)
        return """@{0}.return.{2} //call {0} {1}: push return-address onto stack
    D=A
    @SP
    A=M
    M=D //return-address now on stack
    @SP
    M=M+1 //increment pointer
    @LCL //push local onto stack
    D=M
    @SP
    A=M
    M=D //local now on stack
    @SP
    M=M+1 //increment pointer
    @ARG //push arg onto stack
    D=M
    @SP
    A=M
    M=D //arg now on stack
    @SP
    M=M+1 //increment pointer
    @THIS //push this onto stack
    D=M
    @SP
    A=M
    M=D //this now on stack
    @SP
    M=M+1 //increment pointer
    @THAT //push that onto stack
    D=M
    @SP
    A=M
    M=D //that now on stack
    @SP
    M=M+1 //increment pointer
    @SP //calculate arg position
    D=M
    @{3}
    D=D-A  //D now holds arg position
    @ARG
    M=D //arg is now set
    @SP //set LCL
    D=M
    @LCL
    M=D //LCL is now set
    @{0}
    0;JMP
    ({0}.return.{2}) //return-address
""".format(functionName, numArgs, callNum, n)

    # segmentDict["temp"].format("0").replace("\n", "//return; save return value \n", 1) +
    # "//return value saved \n".join(pop.rsplit("\n", 1))
    #
    # fReturnString = (segmentDict["*local"].replace("\n", "//return; save return address in temp variable \n", 1) + push +
    #                  pushconst.format("5") +
    #                  arithmeticDict["sub"] +
    #                  segmentDict["temp"].format("1") + "//return address saved \n".join(pop.rsplit("\n", 1)) +
    #                  segmentDict["*local"].replace("\n", "//reset <that> \n", 1) + push +
    #                  pushconst.format("1") +
    #                  arithmeticDict["sub"] +
    #                  segmentDict["pointer"].format("1") + "//<that> reset \n".join(pop.rsplit("\n", 1)) +
    #                  segmentDict["*local"].replace("\n", "//reset <this> \n", 1) + push +
    #                  pushconst.format("2") +
    #                  arithmeticDict["sub"] +
    #                  segmentDict["pointer"].format("0") + "//<this> reset \n".join(pop.rsplit("\n", 1)) +
    #                  segmentDict["*local"].replace("\n", "//reset <arg> \n", 1) + push +
    #                  pushconst.format("3") +
    #                  arithmeticDict["sub"] +
    #                  segmentDict["*argument"] + "//<arg> reset \n".join(pop.rsplit("\n", 1)) +
    #                  segmentDict["*local"].replace("//reset <lcl> \n", "\n", 1) + push +
    #                  pushconst.format("4") +
    #                  arithmeticDict["sub"] +
    #                  segmentDict["*local"] + "//<lcl> reset \n".join(pop.rsplit("\n", 1)) +
    #                  segmentDict["*argument"].replace("\n", "//reset <sp> \n", 1) + push +
    #                  pushconst.format("1") +
    #                  arithmeticDict["add"] +
    #                  segmentDict["*stackpointer"] + "//<sp> reset \n".join(pop.rsplit("\n", 1)) +
    #                  "//done return \n".join(
    #                      flowDict["goto"].format("R6").replace("\n", "//goto return \n", 1).rsplit("\n", 1)))

    @classmethod
    def fReturn(cls):
        #return cls.fReturnString
        return """@LCL //return; save local
    D=M
    @R5
    M=D //LCL now saved in R5
    @5
    D=D-A //D=LCL-5
    A=D
    D=M //D=return-address
    @R6
    M=D //return-address now saved in R6
    @SP //get return value
    D=M
    @ARG
    A=M
    M=D //return value now saved in argument position
    D=A+1 //D=ARG+1
    @SP
    M=D //SP now points to ARG+1
    @R5 //Restore THAT
    A=M-1 //A=LCL-1
    D=M //D=saved THAT
    @THAT
    M=D //THAT restored
    @R5 //Restore THIS
    D=M
    @2
    A=D-A //A=LCL-2
    D=M //D=saved THIS
    @THIS
    M=D //THIS = LCL-2
    @R5 //Restore ARG
    D=M
    @3
    A=D-A //A=LCL-3
    D=M //D=saved ARG
    @ARG
    M=D //ARG = LCL-3
    @R5 //Restore LCL
    D=M
    @4
    A=D-A //A=LCL-4
    D=M //D=saved LCL
    @LCL
    M=D //LCL = LCL-4
    @R6
    A=M
    0;JMP //goto return-address
"""

    @classmethod
    def function(cls, functionName, localVars):
        s = "(" + functionName + ")\n"
        locals =  "\n".join(cls.pushconst.format("0") for i in range(int(localVars)))
        if locals:
            s += locals + "\n"
        return s


def main():
    # parser = parse_args(sys.argv[1:])
    folder = sys.argv[1]

    p = parser(folder)
    p.parse()


if __name__ == '__main__':
    main()
