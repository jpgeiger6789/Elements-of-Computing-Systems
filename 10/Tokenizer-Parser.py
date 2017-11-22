#https://docs.python.org/3/howto/argparse.html

import sys
import regex #need to get from pypi - from command line: pip install regex
import os

class tokens():
    #define regular expression patterns
    def __init__(self):
        #find comments in the Jack language
        # the .*? matches as few characters as possible - try to find other matches
        self.multilineCommentStart = r"(?P<multilineCommentStart>" + regex.escape(r"/*") + r".*?)"
        self.multilineCommentEnd = r"(?P<multilineCommentEnd>" + regex.escape(r"*/") + r".*?)"
        self.commentUntilEndofLine = r"(?P<commentUntilEndofLine>(" + regex.escape(r"//") + "|" + regex.escape(r"/*") + ".*?" + regex.escape("*/") + r").*$)"

        #match any of the keywords in the Jack language
        self.keyword = (r"(?P<keyword>(class)|(constructor)|(function)|(method)|(field)|(static)|(var)" +
        r"|(int)|(char)|(boolean)|(void)|(true)|(false)|(null)|(this)|(let)|(do)|(if)|(else)|(while)|(return)(?=\s|$))")

        """
        the symbol regular expression matches the following symbols:
        { } ( ) [ ] . , ; + - * / & | < > = ~
        """
        self.symbol = (r"(?P<symbol>" + "|".join(map(regex.escape, r"{}()[].,;+-*/&|<>=~")) + "(?=\s|$))")

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

        self.LexicalElement = r"(" + r"|".join([self.keyword, self.symbol, self.integerConstant, self.StringConstant, self.identifier]) + r")"

        #the double question mark makes a regex not match if possible
        self.line = (r"^(?P<line>" + self.multilineCommentEnd + "??\s*(" + self.LexicalElement + "\s*)*(" +
                     self.multilineCommentStart + "|" + self.commentUntilEndofLine +")?)$")

if __debug__:
    d = tokens()
    # test to see if the token regexes are working

    #check keywords
    keywords = ("class|constructor|function|method|field|static|var" +
        "|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return").split("|")
    for i in keywords:
        assert regex.match(d.keyword, i)
        assert regex.match(d.LexicalElement, i)

    #check symbols
    for i in r"{}()[].,;+-*/&|<>=~":
        assert regex.match(d.symbol, i)
        assert regex.match(d.LexicalElement, i)

    #check integer constants
    for i in "0|01|10|0123|123|01234|1234|12345|22345|31345|32345|32745|32765|032765|32767".split("|"):
        assert regex.match(d.integerConstant, i)
        assert regex.match(d.LexicalElement, i)
    for i in r"-1|32768|32771|32811|33111|40000|032768|032771|032811|033111|040000|3.4|3.0".split("|"):
        assert not regex.match(d.integerConstant, i)

    #check string constants
    import itertools #need to chain two rainges together
    for i in itertools.chain(range(10), range(11, 32768)): #ignore newline character - Jack language doesn't support it
        assert regex.match(d.StringConstant, '"' + regex.escape(chr(i)) + '"')
        assert regex.match(d.LexicalElement, '"' + regex.escape(chr(i)) + '"')
    assert regex.match(d.StringConstant, '""')
    assert regex.match(d.LexicalElement, '""')
    assert not regex.match(d.StringConstant, 'abc')
    assert  not regex.match(d.StringConstant, '')

    #check lines
    for line in [r'  class foo 12345 + 23456', r'( //this is a comment', r'"howdy" if 00000012 let "let" ; ( ) /* another comment*/']:
        x = regex.match(d.line, line)

        #https://stackoverflow.com/questions/28856238/how-to-get-group-name-of-match-regular-expression-in-python
        lookupDict = [([n for n, v in a.groupdict().items() if v][0], a.group()) for a in regex.finditer(d.LexicalElement, line)]

        print(x.captures())
        print(line)
        print(len(x.groups))
        assert regex.match(d.line, line)

class parser():
    def __init__(self, fname):
        extens = os.path.basename(fname).rsplit(".", 1)[1]
        self.iname = fname
        self.oname = fname[:-len(extens)-1] + ".xml"
        self.tokens = tokens()

    def getTokens(self):
        tokens = dict()
        regExLine = regex.compile(self.tokens.line)
        if os.path.isfile(self.oname):
            os.remove(self.oname)
        with open(self.iname, "r") as inputFile:
            nextline = inputFile.readline()
            while nextline:
                tokenMatch = regex.match(regExLine, nextline)
                if not tokenMatch:
                    raise Exception("TokenizerError", "unparsable line found:/n" + nextline)
                if tokenMatch.groups("multilineCommentEnd"):
                    raise Exception("TokenizerError", "comment end prior to comment start")

                # https://stackoverflow.com/questions/28856238/how-to-get-group-name-of-match-regular-expression-in-python
                #the below list comprehension creates a list of the form [(keyword, class), (integer, 123), ...] matching
                # the tokens found in a given line
                matchlist = [([n for n, v in a.groupdict().items() if v][0], a.group()) for a in
                              regex.finditer(d.LexicalElement, line)]

                firstToken = matchlist[0]
                elementType = firstToken[0]
                elementValue = firstToken[1]
                if elementType == "keyword":
                    if elementValue == "class":
                        parseClass()
                elif elementType == "symbol":
                    raise Exception("TokenizerError", "line begins with symbol:/n" + nextline)
                elif elementType == "integerConstant":
                    foo = 1
                elif elementType == "StringConstant":
                    foo = 1
                elif elementType == "identifier":
                    foo = 1
                nextline = inputFile.readline()
def main():
    #parser = parse_args(sys.argv[1:])
    fname = sys.argv[1]

    p = parser(fname)
    p.parse()

#if __name__ == '__main__':
    #main()