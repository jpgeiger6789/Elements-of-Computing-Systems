@3030 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@THIS //pointer: set R13 to <pointer> sector in memory (index 0 to 1)
    D=A
    @0
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector
@SP //pop:  decrements the stack and then sends the top value in the stack to sector pointed to in R13
    M=M-1  //decrement stack pointer
    @SP
    A=M
    D=M //D now holds top stack value
    @R13
    A=M
    M=D //done pop: sector from R13 now holds the value
@3040 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@THIS //pointer: set R13 to <pointer> sector in memory (index 0 to 1)
    D=A
    @1
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector
@SP //pop:  decrements the stack and then sends the top value in the stack to sector pointed to in R13
    M=M-1  //decrement stack pointer
    @SP
    A=M
    D=M //D now holds top stack value
    @R13
    A=M
    M=D //done pop: sector from R13 now holds the value
@32 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@THIS //this: set R13 to <this> sector in memory (index ??)
    D=M
    @2
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector
@SP //pop:  decrements the stack and then sends the top value in the stack to sector pointed to in R13
    M=M-1  //decrement stack pointer
    @SP
    A=M
    D=M //D now holds top stack value
    @R13
    A=M
    M=D //done pop: sector from R13 now holds the value
@46 //push const: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@THAT //that: set R13 to <that> sector in memory (index ??)
    D=M
    @6
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector
@SP //pop:  decrements the stack and then sends the top value in the stack to sector pointed to in R13
    M=M-1  //decrement stack pointer
    @SP
    A=M
    D=M //D now holds top stack value
    @R13
    A=M
    M=D //done pop: sector from R13 now holds the value
@THIS //pointer: set R13 to <pointer> sector in memory (index 0 to 1)
    D=A
    @0
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector
@R13 //push: sends the value in R13 to the top of the stack and then increments the stack by one
    A=M
    D=M  //D now holds value from sector in R13
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //increment the stack; done push
@THIS //pointer: set R13 to <pointer> sector in memory (index 0 to 1)
    D=A
    @1
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector
@R13 //push: sends the value in R13 to the top of the stack and then increments the stack by one
    A=M
    D=M  //D now holds value from sector in R13
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //increment the stack; done push
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
@THIS //this: set R13 to <this> sector in memory (index ??)
    D=M
    @2
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector
@R13 //push: sends the value in R13 to the top of the stack and then increments the stack by one
    A=M
    D=M  //D now holds value from sector in R13
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //increment the stack; done push
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
@THAT //that: set R13 to <that> sector in memory (index ??)
    D=M
    @6
    D=D+A //D now holds memory value of correct sector
    @R13
    M=D //R13 now holds memory value of correct sector
@R13 //push: sends the value in R13 to the top of the stack and then increments the stack by one
    A=M
    D=M  //D now holds value from sector in R13
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //increment the stack; done push
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
