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
        self.multilineCommentStart = r"(?P<multilineCommentStart>" + regex.escape(r"/*") + r".*$)"
        self.multilineCommentEnd = r"(?P<multilineCommentEnd>^.*?" + regex.escape(r"*/") + r")"
        self.endOfLineComment = r"(?P<endOfLineComment>(" + regex.escape(r"/") * 2 + ".*|" + regex.escape(r"/*") + ".*?" + regex.escape("*/") + r")$)"

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
        self.stringConstant = r'"(?P<stringConstant>.*)"(?=\s|$|' + "|".join(map(regex.escape, r"{}()[].,;+-*/&|<>=~")) + ')'

        self.identifier = r"(?P<identifier>[a-zA-Z_][\w_]*(?=\s|$|" + "|".join(map(regex.escape, r"{}()[].,;+-*/&|<>=~")) + "))"

        self.LexicalElement = r"(" + r"|".join([self.symbol, self.keyword, self.integerConstant, self.stringConstant, self.identifier]) + r")"

        #the double question mark makes a regex not match if possible
        #endOfLineComment must come before multilineCommentStart so it matches first if possible - otherwise multilineCommentStarts will always match,
        #even if they end on the same line.
        #self.line = (r"^" + self.multilineCommentEnd + "??\s*(" + self.endOfLineComment + "|(\s*(" + self.LexicalElement + "\s*)*(" +
        #             self.endOfLineComment + "|" + self.multilineCommentStart +")?))$")
        #since endofLineComment and multilineCommentStart match until the end of the line, it's safe to include them in an or statement with LexicalElement
        #that matches any number of times - Lexical elements will be found until an end of line comment or multilinecommentstart is found.
        self.line = (r"^(\s*" + self.endOfLineComment + ")|(" + self.multilineCommentEnd + "?\s*(" + self.endOfLineComment + "|" + self.multilineCommentStart + "|" + self.LexicalElement + "\s*)*)$")

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

    normalLine = "    static boolean test;    // Added for testing -- there is no static keyword"
    assert regex.match(d.line, normalLine)
    assert regex.match(d.line, normalLine).group("endOfLineComment")

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
    for i in "0|01|10 - completed|0123|123|01234|1234|12345|22345|31345|32345|32745|32765|032765|32767".split("|"):
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
                    raise Exception("TokenizerError", "comment end prior to comment start:\n" + nextline + "\n" + str(list(self.tokenizeLine(nextline))))

                tokenList += [i for i in self.tokenizeLine(nextline) if i[0].find("Comment") < 0]

                if tokenMatch.group("multilineCommentStart"):
                    foundCommentEnd = False
                    lineForErrorMessage = nextline #save this for error handling later
                    nextline = inputFile.readline()
                    while nextline:
                        tokenMatch = regex.match(self.regExLine, nextline)
                        """
                        if tokenMatch:
                            x = list(self.tokenizeLine(nextline))
                            if x:
                                tokenMatch = regex.match(self.regExLine, nextline)
                        """
                        if tokenMatch and tokenMatch.group("multilineCommentEnd"):
                            tokenList += [i for i in self.tokenizeLine(nextline) if i[0].find("Comment") < 0]
                            nextline = inputFile.readline()
                            foundCommentEnd = True
                            break
                        nextline = inputFile.readline()
                    #check to see if we've read to the end of the file without finding a comment end mark
                    if not foundCommentEnd:
                        raise Exception("TokenizerError", "multilineCommentStart without multilineCommentEnd:\nfilename:" + self.iname + "\nline:\n" + lineForErrorMessage)
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

class ParseException(Exception):
    def __init__(self, errMessage, token, tokenList, VMcode, fileName):
        Exception.__init__(self, errMessage)
        self.token = token
        self.tokenList = tokenList
        self.VMcode = VMcode
        self.fileName = fileName

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        baseStr =  Exception.__str__(self)
        if self.tokenList:
            #tokens = "\n".join(str(i[1]) for i in self.tokenList[:self.token[0] + 1])
            tokens = "\n".join(str(i[1]) for i in self.tokenList)
        else:
            tokens = "no tokens found"
        if not self.token:
            self.token = "no token"
        if not self.VMcode:
            self.VMcode = "no VM code"
        return baseStr + "\nfilename: " + self.fileName +  "\nthe tokens are:\n" + tokens + "\nthe VM code is:\n" + self.VMcode + "\ntoken that caused an issue:\n" + str(self.token) + "\n"+ baseStr

"""
identical to Exception but with a new name
"""
class VariableInitException(Exception):
    pass

"""
class to be used in the variable lookup dictionary
"""
class Variable():
    def __init__(self, name, type, kind, num):
        #if any of the properties are missing or incorrect throw an error
        if not (name and type and kind and isinstance(num, int) and num >= 0):
            raise  VariableInitException("all variables must be initialized")
        self.name = name
        self.type = type
        self.kind = kind
        self.num = num

class Parser():
    """
    In each parse subroutine, we will assume the next element has already been selected and verified for the subroutine
    """
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.tokenList = tokenizer.tokenList
        self.tokenIterable = enumerate(self.tokenList) #could be just an iterator, but enumerating it gives the token position for error handling
        self.VMcode = ""
        self.ClassName = ""
        self.nextToken = [None, None] #tokenIndex, token, where token is of the form [tokenType, tokenValue]

    def Parse(self):
        self.nextToken = next(self.tokenIterable)
        if self.nextToken[1][1] != "class":
            raise ParseException("Parse error: the first token must be the keyword 'class'", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
        self.compileClass()

    def compileClass(self):
        self.nextToken = next(self.tokenIterable)
        
        if self.nextToken[1][0] != "identifier":
            raise ParseException("compileClass error: the second token in a class must be an identifier", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
        
        self.ClassName = self.nextToken[1][1]
        
        self.nextToken = next(self.tokenIterable)
        if self.nextToken[1][1] != "{":
            raise ParseException("compileClass error: the third token must be an opening bracket", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        self.nextToken = next(self.tokenIterable)

        variableDict = dict() #name:Variable Class lookup
        num = [0]
        while (self.nextToken[1][1] in ["static", "field"]):
            self.compileVariabledeclaration(num, variableDict) #must call next element before exiting

        while self.nextToken[1][1] in ["constructor", "function", "method"]:
            subEl = ET.SubElement(parent, "subroutineDec")
            subEl.text = "\n"
            #we're going to copy the variableList so it isn't modified by the compileFunction subroutine so we create a union with an empty list
            self.compileFunction(subEl, variableSet.union([])) #must call next element before exiting

        if self.nextToken[1][1] != "}":
                raise ParseException("compileClass error: the final token in a class must be a closing bracket.", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        try:
            self.nextToken = next(self.tokenIterable)
            raise ParseException("compileClass error: the class must end with the closing bracket after all subroutine declarations.", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
        except StopIteration:
            pass

    """
    pass num as a list so it is a mutable object?
    """
    def compileVariabledeclaration(self, num, variableDict):
        kind = self.nextToken[1][1]
        self.nextToken = next(self.tokenIterable)

        if not (self.nextToken[1][0] == "identifier" or self.nextToken[1][1] in ["int", "char", "boolean"]):
            raise ParseException("compileVariabledeclaration error: the first token after a var statement must be a type name", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
        type = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        commaFound = True #this should really be false but we need it to be True to make the loop execute at least once

        while commaFound:
            if self.nextToken[1][0] != "identifier":
                raise ParseException("compileVariabledeclaration error: expected an identifier", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
            name = self.nextToken[1][1]

            variableDict[name] = Variable(name, type, kind, num[0]) #record the variable name to be passed back to the caller
            num[0] += 1
            raise Exception("VM translation not implemented")

            self.nextToken = next(self.tokenIterable)
            if self.nextToken[1][1] not in [",", ";"]:
                raise ParseException("compileVariabledeclaration error: the token after a variable name must be a comma or semicolon", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
            commaFound = (self.nextToken[1][1] == ",") #keep looping until a semicolon is found

            self.nextToken = next(self.tokenIterable)



    """
    variableSet must be a set containing all the class variables so that the function can know what variables are in its scope
    """
    def compileFunction(self, parent, variableSet):
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)
        if not (self.nextToken[1][0] == "identifier" or self.nextToken[1][1] in ["void", "int", "char", "boolean"]):
            raise ParseException("compileFunction error: the token after a function declaration must be 'void' or a type declaration", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)
        if self.nextToken[1][0] != "identifier":
            raise ParseException("compileFunction error: the token after a function type declaration must be an identifier", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)
        if self.nextToken[1][1]  != "(":
            raise ParseException("compileFunction error: the token after the subroutine name must be an opening parenthesis", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)
        subEl = ET.SubElement(parent, "parameterList")
        subEl.text = "\n"
        self.compileParameterList(subEl) #must call next element before exiting

        if self.nextToken[1][1] != ")":
            raise ParseException("compileFunction error: the token after the expression list must be a closing parenthesis", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)
        if self.nextToken[1][1] != "{":
            raise ParseException("compileFunction error: the token after a function name must be a forward bracket '{'", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        subEl = ET.SubElement(parent, "subroutineBody")
        subEl.text = "\n"
        self.compileSubroutineBody(subEl, variableSet) #must call next element before exiting

    def compileParameterList(self, parent):
        if not (self.nextToken[1][0] == "identifier" or self.nextToken[1][1] in ["int", "char", "boolean", ")"]):
            raise ParseException("compileParameterList error: invalid token found.  Expected type declaration or closing parenthesis", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
        continueBool = (self.nextToken[1][1] != ")") #could be an empty parameterlist

        while continueBool:
            if not (self.nextToken[1][0] == "identifier" or self.nextToken[1][1] in ["int", "char", "boolean"]):
                raise ParseException("compileParameterList error: invalid token found.  Expected type declaration", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]

            self.nextToken = next(self.tokenIterable)

            if self.nextToken[1][0] != "identifier":
                raise ParseException("compileParameterList error: each variable name must be an identifier", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]

            self.nextToken = next(self.tokenIterable)
            if not (self.nextToken[1][1] in [",", ")"]):
                raise ParseException("compileParameterList error: the parameterList must end with a parenthesis or be separated by commas.", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
            continueBool = self.nextToken[1][1] == ","
            if continueBool: #if continue, you must first process the next token
                subEl = ET.SubElement(parent, self.nextToken[1][0])
                subEl.text = self.nextToken[1][1]

                self.nextToken = next(self.tokenIterable)

    """
    variableSet must be a set containing all the class variables so that the function can know what variables are in its scope
    """
    def compileSubroutineBody(self, parent, variableSet):
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        while self.nextToken[1][1] == "var":
            subEl = ET.SubElement(parent, "varDec")
            subEl.text = "\n"
            variableSet = variableSet.union(self.compileVariabledeclaration(subEl)) #must call next element before exiting

        subEl = ET.SubElement(parent, "statements")
        subEl.text = "\n"
        self.compileStatements(subEl, variableSet) #must call next element before exiting

        if self.nextToken[1][1] != "}":
                raise ParseException("compileSubroutineBody error: the final token in a function must be a closing bracket.", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

    """
    variableSet must be a set containing all the class variables so that the statements can know what variables are in their scope
    """
    def compileStatements(self, parent, variableSet):
        while self.nextToken[1][1] in ["let", "if", "while", "do", "return"]:
            if self.nextToken[1][1] == "let":
                subEl = ET.SubElement(parent, "letStatement")
                subEl.text = "\n"
                self.compileLetStatement(subEl, variableSet) #must call next element before exiting
            elif self.nextToken[1][1] == "if":
                subEl = ET.SubElement(parent, "ifStatement")
                subEl.text = "\n"
                self.compileIfStatement(subEl, variableSet) #must call next element before exiting
            elif self.nextToken[1][1] == "while":
                subEl = ET.SubElement(parent, "whileStatement")
                subEl.text = "\n"
                self.compileWhileStatement(subEl, variableSet) #must call next element before exiting
            elif self.nextToken[1][1] == "do":
                subEl = ET.SubElement(parent, "doStatement")
                subEl.text = "\n"
                self.compileDoStatement(subEl, variableSet) #must call next element before exiting
            elif self.nextToken[1][1] == "return":
                subEl = ET.SubElement(parent, "returnStatement")
                subEl.text = "\n"
                self.compileReturnStatement(subEl, variableSet) #must call next element before exiting

    def compileLetStatement(self, parent, variableSet):
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)
        if self.nextToken[1][0] != "identifier":
            raise ParseException("compileLetStatement error: the second token in a let statement must be an identifier", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
        if not self.nextToken[1][1] in variableSet:
            raise ParseException("compileLetStatement error: variable not in scope.  Could be a misspelling.", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        #handle an indexed let statement
        if self.nextToken[1][1] == "[":
            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]

            self.nextToken = next(self.tokenIterable)
            subEl = ET.SubElement(parent, "expression")
            subEl.text = "\n"
            self.compileExpression(subEl, variableSet)  #must call next element before exiting

            if self.nextToken[1][1] != "]":
                raise ParseException("compileLetStatement error: an indexed let statement must have a closing bracket after the enclosed expression", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]
            self.nextToken = next(self.tokenIterable)

        if self.nextToken[1][1] != "=":
            raise ParseException("compileLetStatement error: a let statement must have an equals sign after the identifier (and optional index)", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        subEl = ET.SubElement(parent, "expression")
        subEl.text = "\n"
        self.compileExpression(subEl, variableSet)  # must call next element before exiting

        if self.nextToken[1][1] != ";":
            raise ParseException("compileLetStatement error: a let statement must end in a semicolon", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

    def compileIfStatement(self, parent, variableSet):
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        if self.nextToken[1][1] != "(":
            raise ParseException("compileIfStatement error: the second token in an if statement must be a forward parenthesis", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        subEl = ET.SubElement(parent, "expression")
        subEl.text = "\n"
        self.compileExpression(subEl, variableSet)  # must call next element before exiting


        if self.nextToken[1][1] != ")":
            raise ParseException("compileIfStatement error: token following an expression in an if statement must be a closing parenthesis", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)
        if self.nextToken[1][1] != "{":
            raise ParseException("compileIfStatement error: the token following the conditional in an if statement must be a forward bracket", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        subEl = ET.SubElement(parent, "statements")
        subEl.text = "\n"
        self.compileStatements(subEl, variableSet)  # must call next element before exiting

        if self.nextToken[1][1] != "}":
            raise ParseException("compileIfStatement error: the token following the statements in an if statement must be a closing bracket", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        #handle else statement
        if self.nextToken[1][1] == "else":
            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]

            self.nextToken = next(self.tokenIterable)

            if self.nextToken[1][1] != "{":
                raise ParseException("compileIfStatement error: the token following the else keyword in an if statement must be a forward bracket", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]

            self.nextToken = next(self.tokenIterable)

            subEl = ET.SubElement(parent, "statements")
            subEl.text = "\n"
            self.compileStatements(subEl, variableSet)  # must call next element before exiting

            if self.nextToken[1][1] != "}":
                raise ParseException("compileIfStatement error: the token following the statements in an if statement must be a closing bracket", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]

            self.nextToken = next(self.tokenIterable)

    def compileWhileStatement(self, parent, variableSet):
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        if self.nextToken[1][1] != "(":
            raise ParseException("compileWhileStatement error: the second token in a while statement must be a forward parenthesis", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        subEl = ET.SubElement(parent, "expression")
        subEl.text = "\n"
        self.compileExpression(subEl, variableSet)  # must call next element before exiting


        if self.nextToken[1][1] != ")":
            raise ParseException("compileWhileStatement error: token following an expression in a while statement must be a closing parenthesis", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        if self.nextToken[1][1] != "{":
            raise ParseException("compileWhileStatement error: the token following the conditional in a while statement must be a forward bracket", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        subEl = ET.SubElement(parent, "statements")
        subEl.text = "\n"
        self.compileStatements(subEl, variableSet)  # must call next element before exiting

        if self.nextToken[1][1] != "}":
            raise ParseException("compileWhileStatement error: the token following the statements in a while statement must be a closing bracket", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

    def compileDoStatement(self, parent, variableSet):
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        self.compileSubroutineCall(parent, variableSet)  #must call next element before exiting

        if self.nextToken[1][1] != ";":
            raise ParseException("compileDoStatement error: a do statement must end in a semicolon", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

    def compileReturnStatement(self, parent, variableSet):
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        if self.nextToken[1][1] != ";":
            subEl = ET.SubElement(parent, "expression")
            subEl.text = "\n"
            self.compileExpression(subEl, variableSet)  # must call next element before exiting

        if self.nextToken[1][1] != ";":
            raise ParseException("compileReturnStatement error: a return statement must end in a semicolon", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

    def compileExpression(self, parent, variableSet):
        subEl = ET.SubElement(parent, "term")
        subEl.text = "\n"
        self.compileTerm(subEl, variableSet)  #must call next element before exiting

        while self.nextToken[1][1] in ["+", "-", "*", "/", "&", "|", "<", ">", "="]:
            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]

            self.nextToken = next(self.tokenIterable)
            subEl = ET.SubElement(parent, "term")
            subEl.text = "\n"
            self.compileTerm(subEl, variableSet)  #must call next element before exiting

    """
    compileTerm is the only subroutine that will do its own validation internally.  It is only called from the compileExpression function
    so this isn't too big of a deal
    """
    def compileTerm(self, parent, variableSet):
        tokenType = self.nextToken[1][0]
        tokenValue = self.nextToken[1][1]
        if not (tokenType in ["integerConstant", "stringConstant", "identifier"] or tokenValue in ["(", "-", "~", "true", "false", "null", "this"]):
            raise ParseException("compileTerm error: the first token in a term must be one of the following: integer, string, keywordConstant, variable name, " +
                            "subroutine call, opening parenthesis, or unary operation", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        #first handle the terms that are a single token
        if tokenType in ["integerConstant", "stringConstant"]:
            subEl = ET.SubElement(parent, tokenType)
            subEl.text = tokenValue

            self.nextToken = next(self.tokenIterable)
        elif tokenValue in ["true", "false", "null", "this"]:
            subEl = ET.SubElement(parent, "keyword")
            subEl.text = tokenValue

            self.nextToken = next(self.tokenIterable)
        #next handle the terms that are more complicated
        elif tokenValue in ["-", "~"]:
            #unaryOp term
            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]

            self.nextToken = next(self.tokenIterable)
            subEl = ET.SubElement(parent, "term")
            self.compileTerm(subEl, variableSet)  #must call next element before exiting
        elif tokenType == "identifier":
            #could be a standalone term, or it could be an indexed term, or it could be a subroutine call
            self.nextToken = next(self.tokenIterable)
            if not self.nextToken[1][1] in ["[", "(", "."]:
                #must have been a variable name
                subEl = ET.SubElement(parent, "identifier")
                subEl.text = tokenValue
                #we don't iterate the tokenIterable, since we already did that before
                #self.nextToken = next(self.tokenIterable)  <<not required
            elif self.nextToken[1][1] == "[":
                #indexed variable name
                subEl = ET.SubElement(parent, "identifier")
                subEl.text = tokenValue
                subEl = ET.SubElement(parent, self.nextToken[1][0])
                subEl.text = self.nextToken[1][1]
                #got the variable and the opening bracket, now process the enclosed expression
                self.nextToken = next(self.tokenIterable)
                subEl = ET.SubElement(parent, "expression")
                subEl.text = "\n"
                self.compileExpression(subEl, variableSet)
                if self.nextToken[1][1] != "]":
                    raise ParseException("compileTerm error: an indexed variable must end with a closing bracket", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
                subEl = ET.SubElement(parent, self.nextToken[1][0])
                subEl.text = self.nextToken[1][1]
                self.nextToken = next(self.tokenIterable)
            elif self.nextToken[1][1] in ["(", "."]:
                #subroutine call or class-subroutine call
                #send the previous token value to the compile function or it won't know what it was
                self.compileSubroutineCall(parent, variableSet, tokenValue)  #must call next element before exiting
        elif tokenValue == "(":
            #expression
            subEl = ET.SubElement(parent, tokenType)
            subEl.text = tokenValue
            self.nextToken = next(self.tokenIterable)
            subEl = ET.SubElement(parent, "expression")
            subEl.text = "\n"
            self.compileExpression(subEl, variableSet)
            if self.nextToken[1][1] != ")":
                raise ParseException("compileTerm error: an open parentheses in a term must be an expression with a closing parenthesis. Expression was parsed but the following " +
                                    "token was not a closing parenthesis.", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]
            self.nextToken = next(self.tokenIterable)

    """
    previousIdentifier is an optional string to be sent to the function.  You may know off the bat if you're in a subroutine call,
    from the 'do' keyword.  However, if a term is a subroutine, you won't know until you see an opening parenthesis (indicating
    an expression list) or a period (indicating a class call) after an identifier.  In that case, the tokenIterable has already
    moved past the identifierName, so we have to pass it to this function or there would be no way to access it.
    """
    def compileSubroutineCall(self, parent, variableSet, previousIdentifier = ""):
        if not previousIdentifier:
            previousIdentifier = self.nextToken[1][1]
            """
            if the subroutine name is already known, it's because we've already found that the token after it
            is an opening parenthesis.  Therefore, we only get the next token, which should be an opening
            parenthesis, if the subroutine name is unknown.
            """
            self.nextToken = next(self.tokenIterable)

        if self.nextToken[1][1] not in ["(", "."]:
            raise ParseException("compileSubroutineCall error: the token after the first identifier in a subroutine call must be an opening parenthesis or a period", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        if self.nextToken[1][1] == ".":
            #could be a call to a variable assigned to a class, or to a class itself.  need to distinguish between the two.
            """ this was the old way of doing things
            if previousIdentifier in variableSet:
                subEl = ET.SubElement(parent, "varName")
            else:
                subEl = ET.SubElement(parent, "className")
            """
            subEl = ET.SubElement(parent, "identifier")
            subEl.text = previousIdentifier

            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]

            self.nextToken = next(self.tokenIterable)
            if self.nextToken[1][0] != "identifier":
                raise ParseException("compileSubroutineCall error: the token after the period in a class-subroutine call must be an identifier indicating a subroutine name", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]
            self.nextToken = next(self.tokenIterable)
        else:
            subEl = ET.SubElement(parent, "identifier")
            subEl.text = previousIdentifier

        if self.nextToken[1][1]  != "(":
            raise ParseException("compileSubroutineCall error: the token after the subroutine name must be an opening parenthesis", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)

        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]

        self.nextToken = next(self.tokenIterable)

        subEl = ET.SubElement(parent, "expressionList")
        subEl.text = "\n"
        self.compileExpressionList(subEl, variableSet)  #must call next element before exiting

        if self.nextToken[1][1] != ")":
            raise ParseException("compileSubroutineCall error: the token after the expression list must be a closing parenthesis", self.nextToken, self.tokenList, self.VMcode, self.tokenizer.iname)
        subEl = ET.SubElement(parent, self.nextToken[1][0])
        subEl.text = self.nextToken[1][1]
        self.nextToken = next(self.tokenIterable)

    def compileExpressionList(self, parent, variableSet):
        if self.nextToken[1][1] == ")":
            return
        subEl = ET.SubElement(parent, "expression")
        subEl.text = "\n"
        self.compileExpression(subEl, variableSet)  #must call next element before exiting
        while self.nextToken[1][1] == ",":
            subEl = ET.SubElement(parent, self.nextToken[1][0])
            subEl.text = self.nextToken[1][1]

            self.nextToken = next(self.tokenIterable)

            subEl = ET.SubElement(parent, "expression")
            subEl.text = "\n"
            self.compileExpression(subEl, variableSet)  #must call next element before exiting

def prettify(elem):
    """
    Return a pretty-printed XML string for the Element.
    https://pymotw.com/2/xml/etree/ElementTree/create.html
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def createXML(fileName):
    extens = os.path.basename(fileName).rsplit(".", 1)[1]
    oname = fileName[:-len(extens)-1] + "Parsed.xml"

    if os.path.isfile(oname):
        os.remove(oname)

    t = tokenizer(fileName)
    p = Parser(t)
    p.Parse()
    outText = prettify(p.rootXMLElement)
    with open(oname, "w") as ofile:
        ofile.write(outText)
    #modify file contents
    lines = None
    with open(oname, "r") as ifile:
        lines = ifile.readlines()
    with open(oname, "w") as ofile:
        for i in lines[1:]:
            if i.strip():
                ofile.write(i)


def main():
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else: #for debugging
        fname = os.path.dirname(os.path.realpath(__file__)) + r"\arraytest"

    if os.path.isdir(fname):
        for fileName in os.listdir(fname):
            fullName = os.path.join(fname, fileName)
            if os.path.isfile(fullName):
                extens = os.path.basename(fileName).rsplit(".", 1)[1]
                if extens == "jack":
                    createXML(fullName)
    else:
        createXML(fname)

if __name__ == '__main__':
    main()