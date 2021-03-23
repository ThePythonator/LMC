# LMC++
A remake of the original LMC with an expanded instruction set.

# Details
There are two banks of 16 registers of 32 bits, named general purpose (prefix R), and system (prefix S).
System registers are used primarily for holding values such as the instruction and stack pointers, although registers 8-15 are used by LMC++ Extended.

Memory consists of 2^16 slots of 32 bits, and LMC++ Extended implements a stack which starts at the last slot in memory, and grows towards the heap at the start.

# Usage
To create a program, you can create either a .lmc or .lmcx file (depending on whether you are using standard LMC++, or LMC++ Extended). You then need to use the corresponding python file to assemble it into binary (e.g. `LMC++_translator.py program.lmc`, which produces `program.bin`).

To run/emulate a .bin file, it must first be renamed to `program.bin`, and then you need to execute `LMC++.exe`.
