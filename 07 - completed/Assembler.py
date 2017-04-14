#https://docs.python.org/3/howto/argparse.html

import sys
import re
import os

class tokens():
    #define regular expression patterns
    def __init__(self):
        self.variable = r"(?P<variable>[a-zA-Z_.$:][\w_.$:]*)"
        self.comment = r"(?P<comment>//.*$)"
        self.const = r"(?P<const>\d+)"

        self.destDict = {"null":"000",
                         "M":"001",
                         "D":"010",
                         "MD":"011",
                         "A":"100",
                         "AM":"101",
                         "AD":"110",
                         "AMD":"111"}

        self.dest = "(?P<dest>(" + ")|(".join(re.escape(i) for i in self.destDict.keys()) + "))"

        self.jumpDict = {"null":"000",
                         "JGT":"001",
                         "JEQ":"010",
                         "JGE":"011",
                         "JLT":"100",
                         "JNE":"101",
                         "JLE":"110",
                         "JMP":"111"}

        self.jump = "(?P<jump>(" + ")|(".join(re.escape(i) for i in self.jumpDict.keys()) + "))"

        self.symbolDict = {"SP":0,
                           "LCL":1,
                           "ARG":2,
                           "THIS":3,
                           "THAT":4,
                           "SCREEN":16384,
                           "KBD":24576}

        for i in range(16):
            self.symbolDict["R" + str(i)] = i
        self.nextSymbol = 16

        self.predefinedSymbol = "(?P<predefinedSymbol>(" + ")|(".join(re.escape(i) for i in self.symbolDict.keys()) + "))"

        self.symbol = "(?P<symbol>" + self.predefinedSymbol + "|" + self.variable + ")"

        self.compDict = {"0":"0101010",
                         "1":"0111111",
                         "-1":"0111010",
                         "!D":"0001101",
                         "!A":"0110001",
                         "-D":"0001111",
                         "-A":"0110011",
                         "D+1":"0011111",
                         "A+1":"0110111",
                         "D-1":"0001110",
                         "A-1":"0110010",
                         "D+A":"0000010",
                         "D-A":"0010011",
                         "A-D":"0000111",
                         "D&A":"0000000",
                         "D|A":"0010101",
                         "!M":"1110001",
                         "-M":"1110011",
                         "M+1":"1110111",
                         "M-1":"1110010",
                         "D+M":"1000010",
                         "D-M":"1010011",
                         "M-D":"1000111",
                         "D&M":"1000000",
                         "D|M":"1010101"}

        if __debug__:
            for i in self.compDict.keys():
                assert (len(self.compDict[i]) == 7)

        self.comp = "(?P<comp>(" + ")|(".join(re.escape(i) for i in self.compDict.keys())

        #have to add D, A, and M after, or they may be put too early in the regular expression - if D comes before D+M in the self.comp pattern,
        #the regular expression has no way to know that there is a better match

        self.compDict["D"] = "0001100"
        self.compDict["A"] = "0110000"
        self.compDict["M"] = "1110000"

        self.comp +=  "|D|A|M))"

        self.A_Instruction = "(?P<A_Instruction>@(" + self.const + "|" + self.symbol + "))"
        self.C_Instruction = "(?P<C_Instruction>(" + self.dest + "=)?" + self.comp + "(;" + self.jump + ")?)"
        #self.userDefinedSymbol = r"(?P<userDefinedSymbol>\(" + self.variable + "\))"
        self.placeHolder = r"\((?P<placeHolder>[a-zA-Z_.$:][\w_.$:]*)\)"
        #self.placeHolder = r"(?P<placeHolder>^\(\w+\)$)"

        self.line = r"^(?P<line>" + self.A_Instruction + "|" + self.C_Instruction + "|" + self.placeHolder + r")$"

class parser():
    def __init__(self, fname):
        extens = os.path.basename(fname).rsplit(".", 1)[1]
        self.oname = fname[:-len(extens)-1] + ".hack"
        self.tokens = tokens()
        regEx = re.compile(self.tokens.comment)
        #open the file, remove all whitespace and comments, return as a list
        with open(fname, 'r') as file:
            #generator comprehension inside a list comprehension -
            #   remove all comments and whitespaces from each line in the input file
            #   add all items which still exist to the list
            self.lns = [j for j in (regEx.sub("","".join(i.split())) for i in file) if j]
            regEx = re.compile(self.tokens.placeHolder)
            i = 0
            while i < len(self.lns):
                match = regEx.match(self.lns[i])
                if match:
                    p = match.group("placeHolder")
                    self.tokens.symbolDict[p] = i
                    self.lns.pop(i)
                    i -= 1
                i += 1

            self.nextSymbol = self.tokens.nextSymbol

    def parse(self):
        regEx = re.compile(self.tokens.line)
        if os.path.isfile(self.oname):
            os.remove(self.oname)

        with open(self.oname, "a") as o:
            for i in self.lns:
                out = ""
                match = regEx.match(i)
                if not match:
                    raise Exception("Invalid line: \n" + i + "\n" + ";".join(str(ord(j)) for j in i) + "\n" + regEx.pattern)
                if match.group("A_Instruction"):
                    out = "0"
                    if match.group("const"):
                        out += "{0:015b}".format(int(match.group("const")))
                    elif match.group("symbol"):
                        s = match.group("symbol")
                        if not s in self.tokens.symbolDict:
                            self.tokens.symbolDict[s] = self.nextSymbol
                            self.nextSymbol += 1
                        out += "{0:015b}".format(self.tokens.symbolDict[s])
                elif match.group("C_Instruction"):
                    out = "111"
                    out += self.tokens.compDict[match.group("comp")]
                    if match.group("dest"):
                        out += self.tokens.destDict[match.group("dest")]
                    else:
                        out += "000"
                    if match.group("jump"):
                        out += self.tokens.jumpDict[match.group("jump")]
                    else:
                        out += "000"
                elif match.group("placeHolder"):
                    raise Exception("Invalid line: \n" + i)
                else:
                    raise Exception("Invalid line: \n" + i)
                o.write(out + "\n")

def main():
    #parser = parse_args(sys.argv[1:])
    fname = sys.argv[1]

    p = parser(fname)
    p.parse()

if __name__ == '__main__':
    main()