// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.
//The pixels are continuously refreshed from respective bits in an 8K memory-map, located at RAM[16384] - RAM[24575]

// Put your code here.
@16384
D=A
@screenMin
M=D //screenMin=16384

@24575
D=A
@screenMax
M=D //screenMax=24575

@24576
D=A
@keyBoard
M=D //keyBoard=24576

@16384
D=A
@i
M=D //i=16384

@24576
D=M //D>1 if keyboard pressed
@TYPE
D;JGT
(CLEAR)
@i //i holds the ROM number of the pixel to clear
A=M //now A does
M=0 //clear pixel

@i
M=M-1 //goto previous pixel

//check if you need to reset i
@i
D=M
@16384
D=D-A //D=i-16384
@NORESETCLEAR
D;JGE  //if i>=16384, don't need to reset

//reset i to 16384
@16384
D=A
@i
M=D //i=16384
(NORESETCLEAR)

@24576 //check if keyboard pressed
D=M
@CLEAR
D;JLE //if keyboard is not pressed, go back to clear (else continue to the type command)

(TYPE)
@i //i holds the ROM number of the pixel to clear
A=M //now A does
M=-1  //set pixel

@i
M=M+1  //goto next pixel

//check if you need to reset i
@i
D=M
@24575
D=D-A //D=i-24575
@NORESETTYPE
D;JLE //if i <= 24575, don't need to reset
@24575
D=A
@i
M=D //i=24575
(NORESETTYPE)

@24576
D=M
@TYPE
D;JGT

@CLEAR
0;JMP

(END)
@END
0;JMP