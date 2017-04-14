START /WAIT Python VMtranslator.py MemoryAccess/BasicTest/BasicTest.vm
START /WAIT Python Assembler.py MemoryAccess/BasicTest/BasicTest.asm

START /WAIT Python VMtranslator.py MemoryAccess/PointerTest/PointerTest.vm
START /WAIT Python Assembler.py MemoryAccess/PointerTest/PointerTest.asm

START /WAIT Python VMtranslator.py MemoryAccess/StaticTest/StaticTest.vm
START /WAIT Python Assembler.py MemoryAccess/StaticTest/StaticTest.asm

START /WAIT Python VMtranslator.py StackArithmetic/SimpleAdd/SimpleAdd.vm
START /WAIT Python Assembler.py StackArithmetic/SimpleAdd/SimpleAdd.asm

START /WAIT Python VMtranslator.py StackArithmetic/StackTest/StackTest.vm
START /WAIT Python Assembler.py StackArithmetic/StackTest/StackTest.asm