#include "LMC++.hpp"

const uint64_t MEMORY_SIZE = 65536; // slots
const uint8_t REG_COUNT = 16;

uint32_t memory[MEMORY_SIZE] = { 0 };

enum InstructionEnum {
    HLT = 0b00000, // Halt

    LDR = 0b00010, // Load mem into Rn
    STR = 0b00011, // Store Rn into mem

    INP = 0b00100, // Store input in Rn
    OUT = 0b00101, // Output Rn
    CPR = 0b00110, // Copy Rm into Rn
    CPV = 0b00111, // Copy value into Rn

    ADD = 0b01000, // Add Rn to Rm and store in Rn
    SUB = 0b01001, // Sub Rm from Rn and store in Rn
    LSL = 0b01010, // Left shift Rn by value in Rm and store in Rn
    LSR = 0b01011, // Right shift Rn by value in Rm and store in Rn

    AND = 0b01100, // And Rn and Rm and store in Rn
    ORR = 0b01101, // Or Rn and Rm and store in Rn
    XOR = 0b01110, // Xor Rn and Rm and store in Rn
    NOT = 0b01111, // Not Rn and store in Rn

    BRA = 0b10000, // Branch to location mem
    // BRA label/mem  =  CPV S0, label/mem

    BRZ = 0b10010, // Branch to location mem, only if Rn is zero
    BRP = 0b10011 // Branch to location mem, only if Rn is zero or positive
};

struct InstructionStruct {
    uint16_t location;
    uint8_t registers;
    uint8_t instruction;
};

union InstructionUnion
{
    InstructionStruct instruction_struct;
    uint32_t instruction_int;
};

int main() {
    /*
    * Instruction layout:
    * 
    *       XXX XXXXX XXXX XXXX XXXXXXXXXXXXXXXX
    *        3    5     4    4         16
    * 
    *       FLG  CMD   Rn   Rm    mem/location
    */

    int32_t general_registers[REG_COUNT] = { 0 };
    int32_t system_registers[REG_COUNT] = { 0 }; // should be uint?

    InstructionUnion current_instruction = { 0 };

    uint8_t flg0, flg1, flg2;
    uint8_t instruction;

    std::string filename;

    std::cout << "[INP] Enter the program to run: ";

    std::cin >> filename;

    std::cout << "\n";

    if (filename.length() <= 4 || filename.substr(filename.length() - 4, 4) != ".bin") {
        filename += ".bin";
    }

    std::ifstream program;

    // Try opening program from filename
    program.open(".\\" + filename, std::ios::in | std::ios::binary | std::ios::ate);

    if (!program.is_open()) {
        std::cout << "[ERR] Unable to load " << filename << ", trying examples/" << filename << "\n";
        // Try opening program from examples/filename
        program.open(".\\examples\\" + filename, std::ios::in | std::ios::binary | std::ios::ate);
    }

#ifdef TESTING
    // Only used for testing
    if (!program.is_open()) {
        std::cout << "[ERR] Unable to load " << filename << ", trying F:/Repositories/LMC/" << filename << "\n";
        // Try opening program from filename
        program.open("F:\\Repositories\\LMC\\" + filename, std::ios::in | std::ios::binary | std::ios::ate);
    }

    if (!program.is_open()) {
        std::cout << "[ERR] Unable to load " << filename << ", trying full path F:/Repositories/LMC/examples/" << filename << "\n";
        // Try opening program from examples/filename
        program.open("F:\\Repositories\\LMC\\examples\\" + filename, std::ios::in | std::ios::binary | std::ios::ate);
    }
#endif

    if (program.is_open()) {
        std::cout << "[INF] Loaded " << filename << " successfully.\n";

        std::cout << "\n";

        // Load program into memory
        std::streampos size = program.tellg();
        program.seekg(0, std::ios::beg);
        program.read((char*)&memory, size);
        program.close();

        // Start emulation
        current_instruction.instruction_int = memory[system_registers[0] & 0b1111111111111111];
        system_registers[0]++;

        flg0 = current_instruction.instruction_struct.instruction & 0b10000000;
        flg1 = current_instruction.instruction_struct.instruction & 0b01000000;
        flg2 = current_instruction.instruction_struct.instruction & 0b00100000;

        instruction = current_instruction.instruction_struct.instruction & 0b00011111;

        while (instruction != InstructionEnum::HLT) {

            if (instruction == InstructionEnum::LDR) {
                (flg0 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4] = memory[flg2 ? (flg1 ? system_registers : general_registers)[current_instruction.instruction_struct.registers & 0b1111] : current_instruction.instruction_struct.location];
            }
            else if (instruction == InstructionEnum::STR) {
                memory[flg2 ? (flg1 ? system_registers : general_registers)[current_instruction.instruction_struct.registers & 0b1111] : current_instruction.instruction_struct.location] = (flg0 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4];
            }

            else if (instruction == InstructionEnum::INP) {
                std::cout << "[INP] ";
                uint32_t input;
                std::cin >> input;
                while (std::cin.fail()) {
                    std::cout << "[ERR] Must be integer.\n";
                    std::cin.clear();
                    std::cin.ignore(256, '\n');
                    std::cout << "[INP] ";
                    std::cin >> input;
                }
                (flg0 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4] = input;
            }
            else if (instruction == InstructionEnum::OUT) {
                std::cout << "[OUT] " << (flg0 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4] << "\n";
            }

            else if (instruction == InstructionEnum::CPR) {
                (flg0 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4] = (flg1 ? system_registers : general_registers)[current_instruction.instruction_struct.registers & 0b1111];
            }
            else if (instruction == InstructionEnum::CPV) {
                (flg0 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4] = current_instruction.instruction_struct.location;
            }

            else if (instruction == InstructionEnum::ADD) {
                (flg0 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4] += (flg1 ? system_registers : general_registers)[current_instruction.instruction_struct.registers & 0b1111];
            }
            else if (instruction == InstructionEnum::SUB) {
                (flg0 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4] -= (flg1 ? system_registers : general_registers)[current_instruction.instruction_struct.registers & 0b1111];
            }
            else if (instruction == InstructionEnum::LSR) {
                (flg0 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4] >>= (flg1 ? system_registers : general_registers)[current_instruction.instruction_struct.registers & 0b1111];
            }
            else if (instruction == InstructionEnum::LSL) {
                (flg0 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4] <<= (flg1 ? system_registers : general_registers)[current_instruction.instruction_struct.registers & 0b1111];
            }

            else if (instruction == InstructionEnum::AND) {
                (flg0 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4] &= (flg1 ? system_registers : general_registers)[current_instruction.instruction_struct.registers & 0b1111];
            }
            else if (instruction == InstructionEnum::ORR) {
                (flg0 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4] |= (flg1 ? system_registers : general_registers)[current_instruction.instruction_struct.registers & 0b1111];
            }
            else if (instruction == InstructionEnum::XOR) {
                (flg0 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4] ^= (flg1 ? system_registers : general_registers)[current_instruction.instruction_struct.registers & 0b1111];
            }
            else if (instruction == InstructionEnum::NOT) {
                (flg0 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4] = ~(flg1 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4];
            }


            else if (instruction == InstructionEnum::BRA) {
                system_registers[0] = current_instruction.instruction_struct.location;
            }

            else if (instruction == InstructionEnum::BRZ) {
                if ((flg0 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4] == 0) {
                    system_registers[0] = current_instruction.instruction_struct.location;
                }
            }
            else if (instruction == InstructionEnum::BRP) {

                if (((flg0 ? system_registers : general_registers)[current_instruction.instruction_struct.registers >> 4] & (1 << 31)) == 0) {
                    // Must be positive, since negative bit isn't set
                    system_registers[0] = current_instruction.instruction_struct.location;
                }
            }

            else {
                std::cout << "[ERR] Encounted unrecognised instruction " << std::bitset<5>(instruction) << "\n";
            }

            //std::cout << std::bitset<5>(instruction) << "\n";
            //std::cout << std::bitset<32>(current_instruction.instruction_int) << "\n";
            //std::cout << std::bitset<16>(current_instruction.instruction_struct.location) << "\n";

            // Fetch next instruction
            current_instruction.instruction_int = memory[system_registers[0] & 0b1111111111111111];
            system_registers[0]++;

            flg0 = current_instruction.instruction_struct.instruction & 0b10000000;
            flg1 = current_instruction.instruction_struct.instruction & 0b01000000;
            flg2 = current_instruction.instruction_struct.instruction & 0b00100000;

            instruction = current_instruction.instruction_struct.instruction & 0b00011111;
        }
    }
    else {
        std::cout << "[ERR] Unable to load " << filename << "\n";
    }

    //std::cout << "\n[INP] Press ENTER to exit.\n";

    return 0;
}