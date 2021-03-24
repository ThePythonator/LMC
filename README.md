# LMC++
A remake of the original LMC with an expanded instruction set.

# Details
There are two banks of 16 registers of 32 bits, named general purpose (prefix R), and system (prefix S).
System registers are used primarily for holding values such as the instruction and stack pointers, although registers 8-15 are used by LMC++ Extended.

Memory consists of 2^16 slots of 32 bits, and LMC++ Extended implements a stack which starts at the last slot in memory, and grows towards the heap at the start.

# Usage
To create a program, you can create either a `.lmc` or `.lmcx` file (depending on whether you are using standard LMC++, or LMC++ Extended). You then need to use the corresponding python file to assemble it into binary (e.g. `LMC++_tr.py program.lmc`, which produces `program.bin`).

To run/emulate a `.bin` file, it must first be renamed to `program.bin`, and then you need to execute `LMC++.exe`. This executable closes upon completion, so if you want to see the output of a program, you'll need to run it from the command line, or add a dummy input command at the end of the program.

To get started, take a look in the examples folder.

# Instruction Set

`HLT`             -   Halt


`LDR Rn, mem`     -   Load mem into `Rn`

`STR Rn, mem`     -   Store `Rn` into `mem`


`INP Rn`          -   Store input in `Rn`

`OUT Rn`          -   Output `Rn`

`CPR Rn, Rm`      -   Copy `Rm` into `Rn`

`CPV Rn, val`     -   Copy `val` into `Rn`


`ADD Rn, Rm`      -   Add `Rn` to `Rm` and store in `Rn`

`SUB Rn, Rm`      -   Sub `Rm` from `Rn` and store in `Rn`

`LSL Rn, Rm`      -   Left shift `Rn` by value in `Rm` and store in `Rn`

`LSR Rn, Rm`      -   Right shift `Rn` by value in `Rm` and store in `Rn`


`AND Rn, Rm`      -   Bitwise and `Rn` and `Rm` and store in `Rn`

`ORR Rn, Rm`      -   Bitwise or `Rn` and `Rm` and store in `Rn`

`XOR Rn, Rm`      -   Bitwise xor `Rn` and `Rm` and store in `Rn`

`NOT Rn`          -   Bitwise not `Rn` and store in `Rn`


`BRA mem`         -   Branch (jump) to location `mem` (note, this is the same as `CPV S0, label/mem`)


`BRZ Rn mem`      -   Branch to location `mem`, only if `Rn` is zero

`BRP Rn mem`      -   Branch to location `mem`, only if `Rn` is zero or positive


`LDP Rn, Rm`      -   Load the value at location `Rm` into `Rn`
`STP Rn, Rm`      -   Store the value `Rn` at location `Rm`  


`mem` can be a label or an actual memory address, although labels are recommended over memory addresses.
Labels can be any collection of characters, numbers or underscores, but must not start with a number.
Any line can have a label at the start, and this label then represents the location of that instruction in memory.

General purpose registers are accessed using `R0...R15`
System registers are accessed using `S0...S15` - mess with them at your own peril!
