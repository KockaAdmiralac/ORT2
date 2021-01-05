#!/usr/bin/env python
from typing import Dict, List, Optional, Tuple
import sys
import re

if len(sys.argv) < 2:
    print('Potrebno je zadati putanju do datoteke sa programom kao prvi argument komandne linije.')
    exit(1)

# (     0         1               2               3         4          5         6         7     )
# (Instruction, Indir1, Flags(R, #, +, -), Base1(0b, 0x), Number, Base2(b, h), Indir2, Post(+, -))
line_regex = re.compile(r'^\s*(HALT|RTS|RTI|ROR|ROTR|RORC|ROTRC|PUSH|POP|BLEQ|BGREU|BNNG|BGRT|JLEQ|JMP|JSR|LD|ST|ADD|INC|OR|STRFIND)\s*(\()?([R#+-])?(0[bx])?([0-9a-f]+)?(h)?(\))?([+-])?\s*$', re.IGNORECASE)
instructions: List[Tuple[str, Optional[str], Optional[int]]] = []
opcodes: Dict[str, int] = {
    # Bezadresne
    'HALT': 0,
    'RTS': 1,
    'RTI': 2,
    'ROR': 3,
    'ROTR': 3,
    'RORC': 4,
    'ROTRC': 4,
    'PUSH': 5,
    'POP': 6,
    # Uslovni skokovi
    'BLEQ': 16,
    'BGREU': 17, 
    'BNNG': 18,
    'BGRT': 19,
    'JLEQ': 20,
    # Bezuslovni skokovi
    'JMP': 32,
    'JSR': 33,
    # Adresne
    'LD': 48,
    'ST': 49,
    'ADD': 50,
    'INC': 51,
    'OR': 52,
    'STRFIND': 53
}

adrcodes = ['immed', 'memdir', 'memind', 'regind', 'postincr', 'postdec', 'regdir']

with open(sys.argv[1], 'r', encoding='utf-8') as asm_file:
    for line in asm_file:
        if line.strip() == '':
            # Prazna linija
            continue
        line_match = line_regex.match(line)
        if line_match is None:
            print('Sintaksna greška: ', line)
            exit(1)
        instruction, indir1, flags, base1, number, base2, indir2, post = line_match.groups()
        instruction = instruction.upper()
        indir = False
        reg = flags == 'R' or flags == 'r'
        immed = flags == '#'
        branch = instruction.startswith('B')
        jump = instruction.startswith('J')
        # Validacija
        if flags == '-' and not (branch or immed):
            print('Samo instrukcije grananja i neposredno adresiranje mogu da imaju znak operanda:', line)
            exit(1)
        if (indir1 is not None) != (indir2 is not None):
            print('Nedostaje zagrada kod indirektnog adresiranja: ', line)
        if indir1 is not None and indir2 is not None:
            indir = True
        if base1 is not None and base2 is not None:
            print('Zadate su osnove i kao prefiks i kao sufiks:', line)
            exit(1)
        # Određivanje operanda
        operand = None
        if number is not None:
            if opcodes[instruction] < 8:
                print('Bezadresne instrukcije ne primaju operande:', line)
                exit(1)
            base = 10
            if base1 == '0x' or base1 == '0X' or base2 == 'h' or base2 == 'H':
                base = 16
            elif base1 == '0b' or base1 == '0B' or base2 == 'b' or base2 == 'B':
                base = 2
            operand = int(number, base)
            if flags == '-':
                operand = -operand
            if (reg and operand > 15) or (branch and (operand < -128 or operand > 127)) or operand > 65535:
                print('Operand van dozvoljenih granica:', line)
                exit(1)
        # Određivanje načina adresiranja
        adr = None
        if operand is not None and not branch and not jump:
            if immed:
                if indir:
                    print('Neposredno adresiranje ne može da bude indirektno:', line)
                    exit(1)
                adr = 'immed'
            elif reg:
                if indir:
                    if post == '+':
                        adr = 'postincr'
                    elif post == '-':
                        adr = 'postdec'
                    else:
                        adr = 'regind'
                else:
                    if post is None:
                        adr = 'regdir'
                    else:
                        print('Postinkrement i dekrement su podržani samo kod registarskog indirektnog adresiranja:', line)
            elif post is not None:
                print('Postinkrement i dekrement su podržani samo kod registarskog indirektnog adresiranja:', line)
                exit(1)
            elif indir:
                adr = 'memind'
            else:
                adr = 'memdir'
        # Slanje na formatiranje
        instructions.append((instruction, adr, operand))

for instruction, adr, operand in instructions:
    # print(instruction, adr, operand)
    opcode = opcodes[instruction]
    instruction_format = ['{:08b}'.format(opcode)]
    if instruction.startswith('J'):
        # Instrukcije skoka
        formatted_addr = '{:016b}'.format(operand)
        instruction_format.append(formatted_addr[0:8])
        instruction_format.append(formatted_addr[8:])
    elif instruction.startswith('B'):
        # Instrukcije grananja
        operand_format = '{:08b}'.format(operand)
        if operand < 0:
            operand_format = bin(operand & 0xFF)[-8:]
        instruction_format.append(operand_format)
    elif opcode >= 48:
        # Adresne instrukcije
        adrcode = adrcodes.index(str(adr))
        reg = 0
        nonreg = adr == 'immed' or adr == 'memdir' or adr == 'memind'
        if not nonreg and operand is not None:
            reg = operand
        instruction_format.append('{:08b}'.format((adrcode << 4) + reg))
        if nonreg:
            operand_format = '{:016b}'.format(operand)
            if operand < 0:
                operand_format = bin(operand & 0xFFFF)[-16:]
            instruction_format.append(operand_format[0:8])
            instruction_format.append(operand_format[8:])
    if '--binary' in sys.argv:
        print(' '.join(instruction_format))
    else:
        print(' '.join([hex(int(num, 2)).split('x')[1].upper() for num in instruction_format]))
