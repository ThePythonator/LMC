import argparse

ALLOWED_CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789,_'.upper()

LMC_COMMANDS = [
    'HLT', 'LDR', 'STR', 'INP', 'OUT', 'CPR', 'CPV', 'ADD', 'SUB', 'LSR', 'LSL', 'AND', 'ORR', 'XOR', 'NOT', 'BRA', 'BRZ', 'BRP',

    # Extra, 'fake' commands:
    'DAT', 'LDP', 'STP'
]

LMCX_COMMANDS = {

}

class UnsupportedFileTypeError(Exception):
    pass

class LMCXSytaxError(Exception):
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
    # lmcCode = convert_lmcsym(code)
    # lmcName = write_lmc(name, lmcCode)
    # print('Successfully created {file}'.format(file=lmcName))

if __name__ == '__main__':
    main()