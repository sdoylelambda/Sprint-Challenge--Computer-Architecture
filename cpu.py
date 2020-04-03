"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Memory
        self.memory = [0] * 256
        # General-purpose registers
        self.reg = [0] * 8
        # Stack pointers
        self.SP = 7
        # Program counters
        self.PC = 0
        # Memory Address Register
        self.MAR = 0
        # Memory Data Register
        self.MDR = 0
        # Flags
        self.FL = 0

        # Commands
        # Halt
        self.HLT = 0b00000001
        # Load (put)
        self.LDI = 0b10000010
        # Print
        self.PRN = 0b01000111
        # Multiply
        self.MUL = 0b10100010
        # Branch Table
        self.branchtable = {}
        self.branchtable[0b00000001] = self.handle_HLT
        self.branchtable[0b10000010] = self.handle_LDI
        self.branchtable[0b01000111] = self.handle_PRN
        self.branchtable[0b10100010] = self.handle_MUL
        self.branchtable[0b10100000] = self.handle_ADD
        self.branchtable[0b01000101] = self.handle_PUSH
        self.branchtable[0b01000110] = self.handle_POP
        self.branchtable[0b01010000] = self.handle_CALL
        # Return
        self.branchtable[0b00010001] = self.handle_RET

    def load(self, filename):
        """Load a program into memory."""
        try:
            address = 0
            with open(filename) as f:
                for line in f:
                    comment_split = line.split('#')
                    num = comment_split[0].strip()

                    if num == '':
                        continue

                    value = int(num, 2)

                    self.memory[address] = value
                    address += 1
        except FileNotFoundError:
            print(f'{sys.argv[0]}: {filename} not found')
            sys.exit(2)

    def ram_read(self, address):
        return self.memory[address]

    def ram_write(self, address, value):
        self.memory[address] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            #self.fl,
            #self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    # Stops loop
    def handle_HLT(self):
        self.PC = 0
        return 'HLT'

    # Loads
    def handle_LDI(self):
        operand_a = self.PC + 1
        operand_b = self.PC + 2
        address = self.ram_read(operand_a)
        value = self.ram_read(operand_b)
        self.reg[address] = value
        self.PC += 3

    # Print
    def handle_PRN(self):
        address = self.ram_read(self.PC + 1)
        print(self.reg[address])
        self.PC += 2

    # Multiply
    def handle_MUL(self):
        operand_a = self.ram_read(self.PC + 1)
        operand_b = self.ram_read(self.PC + 2)
        self.alu('MUL', (operand_a), (operand_b))
        self.PC += 3

    def handle_ADD(self):
        operand_a = self.ram_read(self.PC + 1)
        operand_b = self.ram_read(self.PC + 2)
        self.alu('ADD', (operand_a), (operand_b))
        self.PC += 3

    def handle_PUSH(self):
        address = self.ram_read(self.PC + 1)
        value = self.reg[address]
        self.reg[self.SP] -= 1
        self.memory[self.reg[7]] = value
        self.PC += 2

    def handle_POP(self):
        address = self.memory[self.PC + 1]
        value = self.memory[self.reg[7]]
        self.reg[address] = value
        self.reg[self.SP] += 1
        self.PC += 2

    def handle_CALL(self):
        return_address = self.PC + 2
        self.reg[self.SP] -= 1
        self.memory[self.reg[self.SP]] = return_address
        address = self.ram_read(self.PC + 1)
        subroutine_address = self.reg[address]
        self.PC = subroutine_address

    # Return
    def handle_RET(self):
        return_address = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1

        self.PC = return_address

    # TO BE COMPLETED

    # Compare operands to see if equal or not
    def handle_CMP(self):
        operand_a = self.ram_read(self.PC + 1)
        operand_b = self.ram_read(self.PC + 2)
        if self.reg[operand_a] == self.reg[operand_b]:
            # Binary 1 == True
            self.FL = 1
        self.PC += 3

    # Unconditional jump - jump to a different instruction, not in order
    def handle_JMP(self):
        pass

    # Jump if Equal - if Equ bits is 1 in the status register
    def handle_JEQ(self):
        pass

    # Jump Not Equal - Jump not zero
    def handle_JNE(self):
        pass

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            IR = self.ram_read(self.PC)
            try:
                return_command = self.branchtable[IR]()
                if return_command == 'HLT':
                    running = False
            except KeyError:
                print(f'Error: Unknown command: {IR}')
                sys.exit(1)