import argparse

ALLOWED_CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789,_'.upper()

LMC_COMMANDS = [
    'HLT', 'LDR', 'STR', 'INP', 'OUT', 'CPR', 'CPV', 'ADD', 'SUB', 'LSR', 'LSL', 'AND', 'ORR', 'XOR', 'NOT', 'BRA', 'BRZ', 'BRP',

    # Extra, 'fake' commands:
    'DAT', 'LDP', 'STP'
]

LMCX_COMMANDS = {
    'SPSH': {
        'parameters': 'R',
        'implementation': [
            'STP <0>, SP',
            'CPV S8, 1',
            'SUB SP, S8'
        ]
    },
    'SPOP': {
        'parameters': 'R',
        'implementation': [
            'CPV S8, 1',
            'ADD SP, S8',
            'LDP <0>, SP'
        ]
    },
    'CALL': {
        'parameters': 'M',
        'implementation': [
            'CPR R8, IP',
            'CPV R9, 6',
            'ADD R8, R9',
            'SPSH R8',
            'BRA <0>'
        ]
    },
    'RTRN': {
        'parameters': '',
        'implementation': [
            'SPOP IP'
        ]
    }
}

ALIASES = {
    'IP': 'S0',
    'SP': 'S1'
}

class UnsupportedFileTypeError(Exception):
    pass

class LMCXSytaxError(Exception):
    pass

class LMCXUnorderedLinesError(Exception):
    pass

class LMCXInvalidLabelError(Exception):
    pass

def main():
    parser = argparse.ArgumentParser(description='Convert a .lmcx file into a .lmc file')
    parser.add_argument('file')
    args = parser.parse_args()
    name = args.file
    run(name)
    
def load_lmcx(name):
    filename = '{name}.lmcx'.format(name=name)
    with open(filename, 'r') as f:
        code = read_lmcx(f.readlines())
    return code
    
def read_lmcx(lines):
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
                    raise LMCXSytaxError(f'Invalid character \'{c}\'.')

            code.append(line.split(' '))

    return code
    
def convert_lmc(code):
    tidy_lines = []

    counter = 0
    for line in code:
        prefix = []

        try:
            int(line[0])
            prefix.append(line[0])
            del line[0]

        except:
            if line[0][0] in '0123456789':
                raise LMCXInvalidLabelError('Labels cannot start with a numerical character.')

        if line[0] not in LMC_COMMANDS and line[0] not in LMCX_COMMANDS.keys():
            # Assume it is a label

            if line[0][0] in '0123456789':
                raise LMCXInvalidLabelError('Labels cannot start with a numerical character.')

            prefix.append(line[0])
            del line[0]

        if len(line) == 0:
            raise LMCXSytaxError('Lines cannot consist of only a label.')

        if line[0] not in LMC_COMMANDS and line[0] not in LMCX_COMMANDS.keys():
            raise LMCXSytaxError('Command must follow an optional label or line number.')

        if line[0] in LMCX_COMMANDS.keys():
            lmcx_command = LMCX_COMMANDS[line[0]]

            lines = mangle(lmcx_command['implementation'], f'_{line[0]}_{counter}')

            params = lmcx_command['parameters'].split(' ') if len(lmcx_command['parameters']) != 0 else []

            if len(params) != len(line) - 1:
                raise LMCXSytaxError(f'Incorrect number of parameters provided for command {line[0]}.')

            for i, param in enumerate(params):
                if len(param.split(',')) != len(line[i + 1].split(',')):
                    raise LMCXSytaxError(f'Incorrect number of parameters provided for command {line[0]}.')

            k = 0
            for i, param in enumerate(params):
                for j, sub in enumerate(param.split(',')):
                    actual = line[i + 1].split(',')[j]

                    if sub == 'R':
                        if actual[0] not in ['R', 'S']:
                            raise LMCXSytaxError(f'Parameter {k} for command {line[0]} must be a register.')
                    # elif sub == 'M':
                    #     if actual[0] not in ['R', 'S']:
                    #         raise LMCXSytaxError(f'Parameter {k} for command {line[0]} must be a memory address.')
                    
                    lines = multi_str_replace(lines, f'<{k}>', actual)
                    k += 1
                    
            lines[0] = ' '.join(prefix) + (' ' if len(prefix) > 0 else '') + lines[0]
            tidy_lines += read_lmcx(lines)

        else:
            tidy_lines.append(prefix + line)

        counter += 1

    tidy_lines = alias_replace(tidy_lines)

    for line in tidy_lines:
        for command in line:
            if command in LMCX_COMMANDS.keys():
                tidy_lines = convert_lmc(tidy_lines)

    return tidy_lines

def format_lmc(tidy_lines):
    return '\n'.join([' '.join(line) for line in tidy_lines])

def mangle(lines, value):
    return multi_str_replace(lines, '<mangle>', value)

def multi_str_replace(lines, a, b):
    return [line.replace(a, b) for line in lines]
    
def alias_replace(lines):
    new_lines = []

    for line in lines:
        new_line = []

        for sub in line:
            splitted = sub.split(',')
            new_sub = []
            
            for item in splitted:
                if item in ALIASES.keys():
                    new_sub.append(ALIASES[item])
                else:
                    new_sub.append(item)

            new_line.append(','.join(new_sub))
        
        new_lines.append(new_line)

    return new_lines
    
def write_lmc(name, code):
    lmcName = '{name}.lmc'.format(name=name)
    with open(lmcName, 'w+') as f:
        f.write(code)

    return lmcName

def run(filename):
    print('[WARNING] Using memory locations instead of labels is not recommended for LMC++ Extended, due to some commands requiring multiple lines.')
    if filename.split('.')[-1] != 'lmcx':
        raise UnsupportedFileTypeError('Unsupported file type {t}'.format(t=filename.split('.')[-1]))

    name = ''.join(filename.split('.')[:-1])
    code = load_lmcx(name)
    lmc_code = convert_lmc(code)
    lmc_code = format_lmc(lmc_code)
    lmc_name = write_lmc(name, lmc_code)
    print('Successfully created {file}'.format(file=lmc_name))

if __name__ == '__main__':
    main()