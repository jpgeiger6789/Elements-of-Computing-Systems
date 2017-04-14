@256
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
(Class1.set)
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
@16 //static: set R13 to <static> sector in memory (index 0)
    D=M
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
@16 //static: set R13 to <static> sector in memory (index 1)
    D=M
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
@0 //push const 0: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
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
(Class1.get)
@16 //static: set R13 to <static> sector in memory (index 0)
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
@16 //static: set R13 to <static> sector in memory (index 1)
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
(Class2.set)
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
@16 //static: set R13 to <static> sector in memory (index 2)
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
@16 //static: set R13 to <static> sector in memory (index 3)
    D=M
    @3
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
@0 //push const 0: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
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
(Class2.get)
@16 //static: set R13 to <static> sector in memory (index 2)
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
@16 //static: set R13 to <static> sector in memory (index 3)
    D=M
    @3
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
(Sys.init)
@6 //push const 6: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@8 //push const 8: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@Class1.set.return.0 //call Class1.set 2: push return-address onto stack
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
    @7
    D=D-A  //D now holds arg position
    @ARG
    M=D //arg is now set
    @SP //set LCL
    D=M
    @LCL
    M=D //LCL is now set
    @Class1.set
    0;JMP
    (Class1.set.return.0) //return-address
@R5 //temp: set R13 to <temp> sector in memory (index 0)
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
@23 //push const 23: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@15 //push const 15: sends the value to the top of the stack and then increments the stack by one
    D=A //D now holds value
    @SP
    A=M
    M=D //the top stack value is now set
    @SP
    M=M+1 //done push: increment the stack
@Class2.set.return.0 //call Class2.set 2: push return-address onto stack
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
    @7
    D=D-A  //D now holds arg position
    @ARG
    M=D //arg is now set
    @SP //set LCL
    D=M
    @LCL
    M=D //LCL is now set
    @Class2.set
    0;JMP
    (Class2.set.return.0) //return-address
@R5 //temp: set R13 to <temp> sector in memory (index 0)
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
@Class1.get.return.0 //call Class1.get 0: push return-address onto stack
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
    @5
    D=D-A  //D now holds arg position
    @ARG
    M=D //arg is now set
    @SP //set LCL
    D=M
    @LCL
    M=D //LCL is now set
    @Class1.get
    0;JMP
    (Class1.get.return.0) //return-address
@Class2.get.return.0 //call Class2.get 0: push return-address onto stack
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
    @5
    D=D-A  //D now holds arg position
    @ARG
    M=D //arg is now set
    @SP //set LCL
    D=M
    @LCL
    M=D //LCL is now set
    @Class2.get
    0;JMP
    (Class2.get.return.0) //return-address
(WHILE)
@WHILE//goto
    0;JMP //done goto
