// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/01/Mux4Way16.tst

load Mux8Way.hdl,
output-file Mux8Way.out,
compare-to Mux8Way.cmp,
output-list a b c d e f g h sel%B2.3.3 out;


set a 1,
set b 0,
set c 0,
set d 0,
set e 0,
set f 0,
set g 0,
set h 0,
set sel 0,
eval,
output;

set a 0,
set b 1,
set sel 1,
eval,
output;

set b 0,
set c 1,
set sel 2,
eval,
output;

set c 0,
set d 1,
set sel 3,
eval,
output;

set d 0,
set e 1,
set sel 4,
eval,
output;

set e 0,
set f 1,
set sel 5,
eval,
output;

set f 0,
set g 1,
set sel 6,
eval,
output;

set g 0,
set h 1,
set sel 7,
eval,
output;

set a 1,
set e 1,
set h 0,
set sel 0,
eval,
output;

set sel 1,
eval,
output;

set b 1,
eval,
output;

set c 1,
set sel 3,
eval,
output;

set d 1,
set e 0,
eval,
output;

set e 1,
set sel 4,
eval,
output;

set h 1,
set sel 6,
eval,
output;

set sel 7,
eval,
output;