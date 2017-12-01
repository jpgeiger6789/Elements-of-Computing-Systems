#https://docs.python.org/3/howto/argparse.html

import sys
import regex #need to get from pypi - from command line: pip install regex
import os
from xml.dom import minidom
import xml.etree.ElementTree as ET

class tokens():
    #define regular expression patterns
    def __init__(self):
        #find comments in the Jack language
        # the .*? matches as few characters as possible - try to find other matches
        self.multilineCommentStart = r"(?P<multilineCommentStart>" + regex.escape(r"/*") + r".*?)"
        self.multilineCommentEnd = r"(?P<multilineCommentEnd>.*?" + regex.escape(r"*/") + r")"
        self.endOfLineComment = r"(?P<endOfLineComment>(" + regex.escape(r"/") * 2 + ".*|" + regex.escape(r"/*") + ".*?" + regex.escape("*/") + r").*$)"

        """
        the symbol regular expression matches the following symbols:
        { } ( ) [ ] . , ; + - * / & | < > = ~
        """
        self.symbol = (r"(?P<symbol>" + "|".join(map(regex.escape, r"{}()[].,;+-*/&|<>=~")) + ")")

        #match any of the keywords in the Jack language
        #must be followed by a space, end of line, or a symbol
        self.keyword = (r"(?P<keyword>(class)|(constructor)|(function)|(method)|(field)|(static)|(var)" +
        r"|(int)|(char)|(boolean)|(void)|(true)|(false)|(null)|(this)|(let)|(do)|(if)|(else)|(while)|(return))(?=\s|$|" + "|".join(map(regex.escape, r"{}()[].,;+-*/&|<>=~")) + ")")

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
        self.integerConstant = r"(?P<integerConstant>0*(\d{1,4}|[0-2]\d{4}|3[0-1]\d{3}|32[0-6]\d{2}|327[0-5]\d|3276[0-7])(?=\s|$|" + "|".join(map(regex.escape, r"{}()[].,;+-*/&|<>=~")) + "))"

        #matches anything between two double quotes
        self.stringConstant = r'(?P<stringConstant>".*"(?=\s|$|' + "|".join(map(regex.escape, r"{}()[].,;+-*/&|<>=~")) + '))'

        self.identifier = r"(?P<identifier>[a-zA-Z_][\w_]*(?=\s|$|" + "|".join(map(regex.escape, r"{}()[].,;+-*/&|<>=~")) + "))"

        self.LexicalElement = r"(" + r"|".join([self.symbol, self.keyword, self.integerConstant, self.stringConstant, self.identifier]) + r")"

        #the double question mark makes a regex not match if possible
        #endOfLineComment must come before multilineCommentStart so it matches first if possible - otherwise multilineCommentStarts will always match,
        #even if they end on the same line.
        self.line = (r"^" + self.multilineCommentEnd + "??\s*(" + self.endOfLineComment + "|(\s*(" + self.LexicalElement + "\s*)*(" +
                     self.endOfLineComment + "|" + self.multilineCommentStart +")?))$")

if __debug__:
    d = tokens()
    # test to see if the token regexes are working

    #check comments
    endOfLineComments = ["//This file is part of ...", "/* test 123 */", "/** test 345 */"]
    for i in endOfLineComments:
        assert regex.match(d.endOfLineComment, i)
        assert regex.match(d.line, i).group("endOfLineComment")
        m = regex.search(d.line, i)
        assert not (m.group("symbol") or m.group("keyword") or m.group("integerConstant") or m.group("stringConstant") or m.group("identifier"))
    assert regex.match(d.multilineCommentStart, "/*foo bar doo wad 123")
    assert regex.match(d.multilineCommentEnd, "foo wad boo */")


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
    for i in r"-1|32768|32771|32811|33111|40000|032768|032771|032811|033111|040000".split("|"):
        assert not regex.match(d.integerConstant, i)

    #check string constants
    import itertools #need to chain two rainges together
    for i in itertools.chain(range(10), range(11, 32768)): #ignore newline character - Jack language doesn't support it
        assert regex.match(d.stringConstant, '"' + regex.escape(chr(i)) + '"')
        assert regex.match(d.LexicalElement, '"' + regex.escape(chr(i)) + '"')
    assert regex.match(d.stringConstant, '""')
    assert regex.match(d.LexicalElement, '""')
    assert not regex.match(d.stringConstant, 'abc')
    assert  not regex.match(d.stringConstant, '')

    #check identifiers
    for i in ["foo", " i ", "abc123", "a_1", "_123"]:
        assert regex.search(d.identifier, i)

    #check lines
    for line in [r'  class foo 12345 + 23456 12345', r'( //this is a comment', r'"howdy" if 00000012 let "let" ; ( ) /* another comment*/', "  function void main( ) {\n"]:
        x = regex.match(d.line, line)
        assert regex.match(d.line, line)

class tokenizer():
    def __init__(self, fname):
        self.iname = fname
        self.tokens = tokens()
        self.regExLine = regex.compile(self.tokens.line)
        self.tokenList = self.getTokenList()

    def tokenizeLine(self, line):
        matches = self.regExLine.match(line)
        #pull out the capture dictionary.  This is a dict of the form the group name: match list
        matchDict = matches.capturesdict()
        lookupDict = dict()
        for groupName in matchDict:
            #for each group in the dictionary, get the starts list.  This list is sorted first to last in terms of
            #capture order, as are the match lists in matchDict
            starts = matches.starts(groupName)
            for i, startIndex in enumerate(starts):
                lookupDict[startIndex] = (groupName, matchDict[groupName][i])
        tokenList = (lookupDict[startIndex] for startIndex in sorted(lookupDict))
        return tokenList

    def getTokenList(self):
        tokenList = []
        with open(self.iname, "r") as inputFile:
            nextline = inputFile.readline()
            while nextline:
                tokenMatch = regex.match(self.regExLine, nextline)
                if not tokenMatch:
                    raise Exception("TokenizerError", "unparsable line found:\n" + nextline)
                if tokenMatch.group("multilineCommentEnd"):
                    raise Exception("TokenizerError", "comment end prior to comment start:\n" + nextline + "\n" + str(tokenMatch.groups("multilineCommentEnd")))

                tokenList += [i for i in self.tokenizeLine(nextline) if i[0].find("Comment") < 0]

                if tokenMatch.group("multilineCommentStart"):
                    foundCommentEnd = False
                    lineForErrorMessage = nextline #save this for error handling later
                    nextline = inputFile.readline()
                    while nextline:
                        tokenMatch = regex.match(regExLine, nextline)
                        if tokenMatch and tokenMatch.group("multilineCommentEnd"):
                            foundCommentEnd = True
                            break
                        nextline = inputFile.readline()
                    #check to see if we've read to the end of the file without finding a comment end mark
                    if not foundCommentEnd:
                        raise Exception("TokenizerError", "multilineCommentStart without multilineCommentEnd:\n" + lineForErrorMessage)
                else:
                    nextline = inputFile.readline()
        return tokenList

    def printToXML(self, oname):
        if os.path.isfile(oname):
            return False

        tree = ET.Element("tokens")

        for token in self.tokenList:
            t = ET.SubElement(tree, token[0])
            t.text = " " + token[1] + " "

        with open(oname, "w") as ofile:
            # ofile.write(ET.tostring(tree, "unicode"))
            ofile.write(prettify(tree))

class Parser():
    """
    In each parse subroutine, we will assume the next element has already been selected and verified for the subroutine
    """
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.tokenList = tokenizer.tokenList
        self.tokenIterable = enumerate(self.tokenList) #could be just an iterator, but enumerating it gives the token position for error handling
        self.rootXMLElement = None
        self.nextToken = [None, None]

    def Parse(self):
        self.nextToken = next(self.tokenIterable)
        if not self.nextToken or self.nextToken[1][1] != "class":
            raise Exception("ParserError", "Parse error: the first token must be the keyword 'class'\nThe offending token is:" + str(self.nextToken))
        self.rootXMLElement = ET.Element("class")
        self.compileClass(self.rootXMLElement)

    def compileClass(self, parent):
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)
        if not self.nextToken or self.nextToken[1][0] != "identifier":
            raise Exception("ParserError", "compileClass error: the second token in a class must be an identifier\nThe offending token is:" + str(self.nextToken))
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)
        if not self.nextToken or self.nextToken[1][1] != "{":
            raise Exception("ParserError", "compileClass error: the third token must be an opening bracket\nThe offending token is:" + str(self.nextToken))
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        while self.nextToken and (self.nextToken[1][0] == "identifier" or self.nextToken[1][1] in ["int", "char", "boolean"]):
            subEl = ET.SubElement(parent, "classVarDec")
            self.compileVariabledeclaration(subEl) #must call next element before exiting

        while self.nextToken and self.nextToken[1][1] in ["constructor", "function", "method"]:
            subEl = ET.SubElement(parent, "subroutineDec")
            self.compileFunction(subEl) #must call next element before exiting

        if not (self.nextToken and self.nextToken[1][1] == "}"):
                raise Exception("ParserError", "compileClass error: the final token in a class must be a closing bracket.\nThe offending token is:" + str(self.nextToken))

    def compileVariabledeclaration(self, parent):
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        commaFound = True #this should really be false but we need it to be True to make the loop execute at least once

        while commaFound:
            self.nextToken = next(self.tokenIterable)
            if not self.nextToken or self.nextToken[1][0] != "identifier":
                raise Exception("ParserError", "compileVariabledeclaration error: the token after a variable declaration must be an identifier\nThe offending token is:" + str(self.nextToken))
            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]

            self.nextToken = next(self.tokenIterable)
            if not self.nextToken or self.nextToken[1][1] not in [",", ";"]:
                raise Exception("ParserError", "compileVariabledeclaration error: the token after a variable name must be a comma or semicolon\nThe offending token is:" + str(self.nextToken))
            commaFound = (self.nextToken[1][1] == ",") #keep looping until a semicolon is found
            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]

            self.nextToken = next(self.tokenIterable)

    def compileFunction(self, parent):
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)
        if not self.nextToken or not (self.nextToken[1][1] == "identifier" or self.nextToken[1][0] in ["void", "int", "char", "boolean"]):
            raise Exception("ParserError", "compileFunction error: the token after a function declaration must be 'void' or a type declaration\nThe offending token is:" + str(self.nextToken))
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)
        if not self.nextToken or self.nextToken[1][0] != "identifier":
            raise Exception("ParserError", "compileFunction error: the token after a function type declaration must be an identifier\nThe offending token is:" + str(self.nextToken))
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)
        if not self.nextToken or self.nextToken[1][0] != "{":
            raise Exception("ParserError", "compileFunction error: the token after a function name must be a forward bracket '{'\nThe offending token is:" + str(self.nextToken))

        subEl = ET.SubElement(parent, "subroutineBody")
        self.compileFunctionBody(subEl)

    def compileFunctionBody(self, parent):
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        while self.nextToken and (self.nextToken[1][0] == "identifier" or self.nextToken[1][1] in ["int", "char", "boolean"]):
            subEl = ET.SubElement(parent, "varDec")
            self.compileVariabledeclaration(subEl) #must call next element before exiting

        subEl = ET.SubElement(parent, "statements")
        self.compileStatements(subEl) #must call next element before exiting

        if not (self.nextToken and self.nextToken[1][1] == "}"):
                raise Exception("ParserError", "compileFunctionBody error: the final token in a function must be a closing bracket.\nThe offending token is:" + str(self.nextToken))

    def compileStatements(self, parent):
        while self.nextToken and self.nextToken[1][1] in ["let", "if", "while", "do", "return"]:
            if self.nextToken[1][1] == "let":
                subEl = ET.SubElement(parent, "letStatement")
                self.compileVariabledeclaration(subEl) #must call next element before exiting
            elif self.nextToken[1][1] == "if":
                subEl = ET.SubElement(parent, "ifStatement")
                self.compileVariabledeclaration(subEl) #must call next element before exiting
            elif self.nextToken[1][1] == "while":
                subEl = ET.SubElement(parent, "whileStatement")
                self.compileVariabledeclaration(subEl) #must call next element before exiting
            elif self.nextToken[1][1] == "do":
                subEl = ET.SubElement(parent, "doStatement")
                self.compileVariabledeclaration(subEl) #must call next element before exiting
            elif self.nextToken[1][1] == "return":
                subEl = ET.SubElement(parent, "returnStatement")
                self.compileVariabledeclaration(subEl) #must call next element before exiting

    def compileLetStatement(self, parent):
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)
        if not self.nextToken or self.nextToken[1][0] != "identifier":
            raise Exception("ParserError",
                            "compileLetStatement error: the second token in a let statement must be an identifier\nThe offending token is:" +
                            str(self.nextToken))
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        #handle an indexed let statement
        if self.nextToken and self.nextToken[1][1] == "[":
            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]

            self.nextToken = next(self.tokenIterable)
            subEl = ET.SubElement(parent, "expression")
            self.compileExpression(parent)  #must call next element before exiting

            if not self.nextToken or self.nextToken[1][1] != "]":
                raise Exception("ParserError",
                                "compileLetStatement error: an indexed let statement must have a closing bracket after the enclosed expression\nThe offending token is:" +
                                str(self.nextToken))
            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]
            self.nextToken = next(self.tokenIterable)

        if not self.nextToken or self.nextToken[1][1] != "=":
            raise Exception("ParserError",
                            "compileLetStatement error: a let statement must have an equals sign after the identifier (and optional index)\nThe offending token is:" +
                            str(self.nextToken))
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        subEl = ET.SubElement(parent, "expression")
        self.compileExpression(parent)  # must call next element before exiting

        if not self.nextToken or self.nextToken[1][1] != ";":
            raise Exception("ParserError",
                            "compileLetStatement error: a let statement must end in a semicolon\nThe offending token is:" +
                            str(self.nextToken))
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

    def compileIfStatement(self, parent):
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        if not self.nextToken or self.nextToken[1][0] != "(":
            raise Exception("ParserError",
                            "compileIfStatement error: the second token in an if statement must be a forward parenthesis\nThe offending token is:" +
                            str(self.nextToken))
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

    def compileWhileStatement(self, parent):
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

    def compileDoStatement(self, parent):
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

    def compileReturnStatement(self, parent):
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

    def compileExpression(self, parent):
        subEl = ET.SubElement(parent, "term")
        self.compileTerm(subEl)  #must call next element before exiting

        while self.nextToken and self.nextToken in ["+", "-", "*", "/", "&", "|", "<", ">", "="]:
            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]

            self.nextToken = next(self.tokenIterable)
            self.compileTerm(subEl)  #must call next element before exiting

    """
    compileTerm is the only subroutine that will do its own validation internally.  It is only called from the compileExpression function
    so this isn't too big of a deal
    """
    def compileTerm(self, parent):


def prettify(elem):
    """
    Return a pretty-printed XML string for the Element.
    https://pymotw.com/2/xml/etree/ElementTree/create.html
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def main():
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        fname = os.path.dirname(os.path.realpath(__file__)) + r"\ArrayTest\Main.jack"

    extens = os.path.basename(fname).rsplit(".", 1)[1]
    oname = fname[:-len(extens)-1] + " tokenized.xml"

    if os.path.isfile(oname):
        os.remove(oname)

    t = tokenizer(fname)
    t.printToXML()


if __name__ == '__main__':
    main()