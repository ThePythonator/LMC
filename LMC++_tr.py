import argparse, struct

ALLOWED_CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789,_'.upper()

COMMANDS = {
    'HLT': 0,

    'LDR': 2,
    'STR': 3,

    'INP': 4,
    'OUT': 5,
    'CPR': 6,
    'CPV': 7,
    
    'ADD': 8,
    'SUB': 9,
    'LSR': 10,
    'LSL': 11,
    
    'AND': 12,
    'ORR': 13,
    'XOR': 14,
    'NOT': 15,
    
    'BRA': 16,
    
    'BRZ': 18,
    'BRP': 19,

    # Extra, 'fake' commands:
    'DAT': 0,
    'LDP': 2,
    'STP': 3
}

class UnsupportedFileTypeError(Exception):
    pass

class LMCSytaxError(Exception):
    pass

class LMCUnorderedLinesError(Exception):
    pass

class LMCInvalidLabelError(Exception):
    pass

def load_lmc(name):
    filename = '{name}.lmc'.format(name=name)
    with open(filename, 'r') as f:
        code = read_lmc(f.readlines())
    return code

def read_lmc(lines):
    code = []
    for line in lines:
        while '  ' in line:
            line = line.replace('  ', ' ')
            
        line = line.replace(' ,', ',')
        line = line.replace(', ', ',')

        line = line.replace('\t', '')

        if '//' in line:
            index = line.find('//')
            line = line[:index]
        
        line = line.strip().upper()

        if line != '':
            for c in line:
                if c not in ALLOWED_CHARS and c != ' ':
                    raise LMCSytaxError(f'Invalid character \'{c}\'.')

            code.append(line.split(' '))

    return code

def write_bin(name, code):
    bin_name = '{name}.bin'.format(name=name)
    with open(bin_name, 'wb+') as f:
        f.write(bytes(code))

    return bin_name

def resolve_labels(code):
    # Only LDR and STR use labels at end of line
    # Initialise memory
    resolved_code = [['HLT']] * (2**16)

    labels = {}

    index = 0

    for line in code:
        try:
            ID = int(line[0])
            del line[0]
        except:
            ID = index
            if line[0][0] in '0123456789':
                raise LMCInvalidLabelError('Labels cannot start with a numerical character.')
        
        if ID < index:
            raise LMCUnorderedLinesError('Line numbers must be in order.')

        index = ID

        if line[0] not in COMMANDS.keys():
            # Assume it is a label

            if line[0][0] in '0123456789':
                raise LMCInvalidLabelError('Labels cannot start with a numerical character.')

            if line[0] in labels.keys():
                raise LMCInvalidLabelError(f'Label \'{line[0]}\' already exists.')

            labels[line[0]] = index
            del line[0]

        if line[0] not in COMMANDS.keys():
            raise LMCSytaxError('Command must follow an optional label or line number.')


        if len(line) == 0:
            raise LMCSytaxError('Lines cannot consist of only a label.')

        resolved_code[index] = line

        index += 1

    
    index = 0
    for line in resolved_code:
        for i, word in enumerate(line):
            if word in labels.keys() and ',' not in word:
                line[i] = str(labels[word])
            else:
                splitted = word.split(',')
                for j, sub in enumerate(splitted):
                    if sub in labels.keys():
                        splitted[j] = str(labels[sub])

                line[i] = ','.join(splitted)
        
        
        resolved_code[index] = line
        
        index += 1

    return resolved_code

def convert_lmc(code):
    bin_code = []
    for line in code:
        command = line[0]

        if command not in COMMANDS.keys():
            raise LMCSytaxError(f'Command {command} does not exist.')

        bin_line = COMMANDS[command] * (2 ** 24)

        if command in ['CPR', 'ADD', 'SUB', 'LSL', 'LSR', 'AND', 'ORR', 'XOR', 'LDP', 'STP']:
            if len(line) != 2 or len(line[1].split(',')) != 2:
                raise LMCSytaxError(f'Usage is {command} Rn, Rm')

            sub = line[1].split(',')
            if sub[0][0] not in ['R', 'S'] or sub[1][0] not in ['R', 'S']:
                raise LMCSytaxError(f'Usage is {command} Rn, Rm')

            try:
                r_n = int(sub[0][1:])
                r_m = int(sub[1][1:])

            except ValueError:
                raise LMCSytaxError(f'Usage is {command} Rn, Rm')

            if r_n < 0 or r_m < 0 or r_n > 15 or r_m > 15:
                raise LMCSytaxError(f'Register IDs must be in the range 0-15 inclusive.')

            bin_line += r_n * (2 ** 20)
            bin_line += r_m * (2 ** 16)


            # Set flags
            if sub[0][0] == 'S':
                bin_line += 2 ** 31
                
            if sub[1][0] == 'S':
                bin_line += 2 ** 30

            if command in ['LDP', 'STP']:
                bin_line += 2 ** 29

        elif command in ['LDR', 'STR', 'CPV']:
            if len(line) != 2 or len(line[1].split(',')) != 2:
                raise LMCSytaxError(f'Usage is {command} Rn, mem/label')

            sub = line[1].split(',')
                
            try:
                r_n = int(sub[0][1:])

            except ValueError:
                raise LMCSytaxError(f'Usage is {command} Rn, mem/label')
            
            bin_line += r_n * (2 ** 20)
            
            # Set flags
            if sub[0][0] == 'S':
                bin_line += 2 ** 31

            try:
                val = int(sub[1])

            except ValueError:
                raise LMCSytaxError(f'Usage is {command} Rn, mem/label')
                
            bin_line += val

        elif command in ['BRZ', 'BRP']:
            if len(line) != 3:
                raise LMCSytaxError(f'Usage is {command} Rn mem/label')
                
            if line[1][0] not in ['R', 'S']:
                raise LMCSytaxError(f'Usage is {command} Rn mem/label')

            try:
                r_n = int(line[1][1:])

            except ValueError:
                raise LMCSytaxError(f'Usage is {command} Rn mem/label')
            
            bin_line += r_n * (2 ** 20)

            # Set flags
            if line[1][0] == 'S':
                bin_line += 2 ** 31


            try:
                val = int(line[2])

            except ValueError:
                raise LMCSytaxError(f'Usage is {command} Rn mem/label')
                
            bin_line += val

        elif command in ['INP', 'OUT', 'NOT']:
            if len(line) != 2:
                raise LMCSytaxError(f'Usage is {command} Rn')

            if line[1][0] not in ['R', 'S']:
                raise LMCSytaxError(f'Usage is {command} Rn')

            try:
                r_n = int(line[1][1:])

            except ValueError:
                raise LMCSytaxError(f'Usage is {command} Rn')
            
            bin_line += r_n * (2 ** 20)

            # Set flags
            if line[1][0] == 'S':
                bin_line += 2 ** 31

        elif command in ['BRA']:
            if len(line) != 2:
                raise LMCSytaxError(f'Usage is {command} mem/label')

                
            try:
                val = int(line[1])

            except ValueError:
                raise LMCSytaxError(f'Usage is {command} mem/label')
                
            bin_line += val

        elif command in ['DAT']:
            if len(line) != 2:
                raise LMCSytaxError(f'Usage is {command} value')

            try:
                val = int(line[1])

            except ValueError:
                raise LMCSytaxError(f'Usage is {command} value')

            bin_line += val

        bin_code += struct.pack('<I', bin_line)

    return bytearray(bin_code)

def main():
    parser = argparse.ArgumentParser(description='Convert a .lmc file into a .bin file')
    parser.add_argument('file')
    args = parser.parse_args()
    name = args.file
    run(name)

def run(filename):
    if filename.split('.')[-1] != 'lmc':
        raise UnsupportedFileTypeError('Unsupported file type {t}'.format(t=filename.split('.')[-1]))

    name = ''.join(filename.split('.')[:-1])
    code = load_lmc(name)
    resolved_code = resolve_labels(code)
    # print(resolved_code[:10])
    bin_code = convert_lmc(resolved_code)
    # print(bin_code[:40])
    bin_name = write_bin(name, bin_code)
    print('Successfully created {file}'.format(file=bin_name))
    

if __name__ == '__main__':
    main()