(SimpleFunction.test)
@0 //push const 0: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack

@0 //push const 0: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack

@LCL //local: set R13 to <local> sector in memory (index 0)
    D=M
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
@LCL //local: set R13 to <local> sector in memory (index 1)
    D=M
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
@SP //bitwise not
    M=M-1 //leave stack+1 as-is
    A=M
    M=!M //done bitwise not
    @SP
    M=M+1 //increment stack
@ARG //argument: set R13 to <argument> sector in memory (index 0)
    D=M
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
@ARG //argument: set R13 to <argument> sector in memory (index 1)
    D=M
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
@LCL //return; save local
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
