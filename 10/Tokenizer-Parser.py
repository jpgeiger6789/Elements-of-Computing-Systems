#https://docs.python.org/3/howto/argparse.html

import sys
import re
import os

class tokens():
    #define regular expression patterns
    def __init__(self):
        #match any of the keywords in the Jack language
        self.keyword = (r"(?P<keyword>(class)|(constructor)|(function)|(method)|(field)|(static)|(var)" +
        r"|(int)|(char)|(boolean)|(void)|(true)|(false)|(null)|(this)|(let)|(do)|(if)|(else)|(while)|(return)(?=\s|$))")

        """
        the symbol regular expression matches the following symbols:
        { } ( ) [ ] . , ; + - * / & | < > = ~
        """
        self.symbol = (r"(?P<symbol>" + "|".join(map(re.escape, r"{}()[].,;+-*/&|<>=~")) + ")")

        """
        the integerConstant regular expression matches any number in the range 0..32767.  I have allowed any number
        of preceeding zeros to match an integer constant.  Following the regular expression left to right, it will
        match:
        0* = any number of preceeding zeros
        \d{1,4} = any 1 to 4 digit number
        [0-2]\d{4} = any 5 digit number starting with 0 through 2
        3[0-1]\d{3} = any 5 digit number starting with 3 then 0 through 1
        32[0-6]\d{2} = any 5 digit number starting with 32 then 0 through 6
        327[0-5]\d = any 5 digit number starting with 327 then 0 through 5
        3276[0-7] any 5 digit number starting with 3276 and ending with 0 through 7
        (?=\s): must be followed by whitespace or the end of the string
        """
        self.integerConstant = r"(?P<integerConstant>0*(\d{1,4}|[0-2]\d{4}|3[0-1]\d{3}|32[0-6]\d{2}|327[0-5]\d|3276[0-7])(?=\s|$))"

        #matches anything between two double quotes
        self.StringConstant = r'(?P<StringConstant>".*"(?=\s|$))'

        self.identifier = r"(?P<identifier>[a-zA-Z_][\w_]*(?=\s|$))"

        self.LexicalElement = r"(?P<LexicalElement>" + r"|".join([self.keyword, self.symbol, self.integerConstant, self.StringConstant, self.identifier]) + r")"
        self.line = r"(?P<line>^\s*[(" + self.LexicalElement + ")\s*]*$)"

if __debug__:
    d = tokens()
    # test to see if the token regexes are working

    #check keywords
    keywords = ("class|constructor|function|method|field|static|var" +
        "|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return").split("|")
    for i in keywords:
        assert re.match(d.keyword, i)

    #check symbols
    for i in r"{}()[].,;+-*/&|<>=~":
        assert re.match(d.symbol, i)

    #check integer constants
    for i in "0|01|10|0123|123|01234|1234|12345|22345|31345|32345|32745|32765|032765|32767".split("|"):
        assert re.match(d.integerConstant, i)
    for i in r"-1|32768|32771|32811|33111|40000|032768|032771|032811|033111|040000|3.4|3.0".split("|"):
        assert not re.match(d.integerConstant, i)

    #check string constants
    import itertools #need to chain two rainges together
    for i in itertools.chain(range(10), range(11, 32768)): #ignore newline character - Jack language doesn't support it
        assert re.match(d.StringConstant, '"' + re.escape(chr(i)) + '"')
    assert re.match(d.StringConstant, '""')
    assert not re.match(d.StringConstant, 'abc')
    assert  not re.match(d.StringConstant, '')

    #check lines
    for i in [r'  class foo 12345', r'(', r'"howdy" if 00000012 let "let" ; ( ) ']:
        try:
            assert re.match(d.line, i)
        except:
            print(i)


class parser():
    def __init__(self, fname):
        extens = os.path.basename(fname).rsplit(".", 1)[1]
        self.oname = fname[:-len(extens)-1] + ".xml"
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

#if __name__ == '__main__':
    #main()