@17 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@17 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@SP //test equality
    M=M-1 //leave stack+2 as-is
    A=M
    D=-M //D = -y
    @SP
    M=M-1 //leave stack+1 as-is
    A=M
    D=D+M //D = -y + x
    @EQUAL0
    D;JEQ //if D = 0, jump
    @SP
    A=M
    M=0 //false indicated by 0
    @DONETESTEQUALITY0
    0;JMP
    (EQUAL0)
    @SP
    A=M
    M=-1 //true indicated by -1
    (DONETESTEQUALITY0) //done test equality
    @SP
    M=M+1 //increment stack
@17 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@16 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@SP //test equality
    M=M-1 //leave stack+2 as-is
    A=M
    D=-M //D = -y
    @SP
    M=M-1 //leave stack+1 as-is
    A=M
    D=D+M //D = -y + x
    @EQUAL1
    D;JEQ //if D = 0, jump
    @SP
    A=M
    M=0 //false indicated by 0
    @DONETESTEQUALITY1
    0;JMP
    (EQUAL1)
    @SP
    A=M
    M=-1 //true indicated by -1
    (DONETESTEQUALITY1) //done test equality
    @SP
    M=M+1 //increment stack
@16 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@17 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@SP //test equality
    M=M-1 //leave stack+2 as-is
    A=M
    D=-M //D = -y
    @SP
    M=M-1 //leave stack+1 as-is
    A=M
    D=D+M //D = -y + x
    @EQUAL2
    D;JEQ //if D = 0, jump
    @SP
    A=M
    M=0 //false indicated by 0
    @DONETESTEQUALITY2
    0;JMP
    (EQUAL2)
    @SP
    A=M
    M=-1 //true indicated by -1
    (DONETESTEQUALITY2) //done test equality
    @SP
    M=M+1 //increment stack
@892 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@891 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@SP //test less than
    M=M-1 //leave stack+2 as-is
    A=M
    D=-M //D = -y
    @SP
    M=M-1 //leave stack+1 as-is
    A=M
    D=D+M //D = -y + x
    @LESSTHAN0
    D;JLT //if D < 0, jump
    @SP
    A=M
    M=0 //false indicated by 0
    @DONELESSTHAN0
    0;JMP
    (LESSTHAN0)
    @SP
    A=M
    M=-1 //true indicated by -1
    (DONELESSTHAN0) //done test less than
    @SP
    M=M+1 //increment stack
@891 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@892 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@SP //test less than
    M=M-1 //leave stack+2 as-is
    A=M
    D=-M //D = -y
    @SP
    M=M-1 //leave stack+1 as-is
    A=M
    D=D+M //D = -y + x
    @LESSTHAN1
    D;JLT //if D < 0, jump
    @SP
    A=M
    M=0 //false indicated by 0
    @DONELESSTHAN1
    0;JMP
    (LESSTHAN1)
    @SP
    A=M
    M=-1 //true indicated by -1
    (DONELESSTHAN1) //done test less than
    @SP
    M=M+1 //increment stack
@891 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@891 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@SP //test less than
    M=M-1 //leave stack+2 as-is
    A=M
    D=-M //D = -y
    @SP
    M=M-1 //leave stack+1 as-is
    A=M
    D=D+M //D = -y + x
    @LESSTHAN2
    D;JLT //if D < 0, jump
    @SP
    A=M
    M=0 //false indicated by 0
    @DONELESSTHAN2
    0;JMP
    (LESSTHAN2)
    @SP
    A=M
    M=-1 //true indicated by -1
    (DONELESSTHAN2) //done test less than
    @SP
    M=M+1 //increment stack
@32767 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@32766 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@SP //test greater than
    M=M-1 //leave stack+2 as-is
    A=M
    D=-M //D = -y
    @SP
    M=M-1 //leave stack+1 as-is
    A=M
    D=D+M //D = -y + x
    @GREATERTHAN0
    D;JGT //if D > 0, jump
    @SP
    A=M
    M=0 //false indicated by 0
    @DONEGREATERTHAN0
    0;JMP
    (GREATERTHAN0)
    @SP
    A=M
    M=-1 //true indicated by -1
    (DONEGREATERTHAN0) //done test greater than
    @SP
    M=M+1 //increment stack
@32766 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@32767 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@SP //test greater than
    M=M-1 //leave stack+2 as-is
    A=M
    D=-M //D = -y
    @SP
    M=M-1 //leave stack+1 as-is
    A=M
    D=D+M //D = -y + x
    @GREATERTHAN1
    D;JGT //if D > 0, jump
    @SP
    A=M
    M=0 //false indicated by 0
    @DONEGREATERTHAN1
    0;JMP
    (GREATERTHAN1)
    @SP
    A=M
    M=-1 //true indicated by -1
    (DONEGREATERTHAN1) //done test greater than
    @SP
    M=M+1 //increment stack
@32766 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@32766 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@SP //test greater than
    M=M-1 //leave stack+2 as-is
    A=M
    D=-M //D = -y
    @SP
    M=M-1 //leave stack+1 as-is
    A=M
    D=D+M //D = -y + x
    @GREATERTHAN2
    D;JGT //if D > 0, jump
    @SP
    A=M
    M=0 //false indicated by 0
    @DONEGREATERTHAN2
    0;JMP
    (GREATERTHAN2)
    @SP
    A=M
    M=-1 //true indicated by -1
    (DONEGREATERTHAN2) //done test greater than
    @SP
    M=M+1 //increment stack
@57 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@31 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@53 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@SP //add
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
@112 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@SP //subtract
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
@SP //negative
    M=M-1 //leave stack+1 as-is
    A=M
    M=-M //done negative
    @SP
    M=M+1 //increment stack
@SP //bitwise and
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
@82 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@SP //bitwise or
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
@SP //bitwise not
    M=M-1 //leave stack+1 as-is
    A=M
    M=!M //done bitwise not
    @SP
    M=M+1 //increment stack
