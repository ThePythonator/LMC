import argparse

class UnsupportedFileTypeError(Exception):
    pass

def main():
    parser = argparse.ArgumentParser(description='Convert a .lmcx file into a .lmc file')
    parser.add_argument('file')
    args = parser.parse_args()
    name = args.file
    run(name)

def run(filename):
    print('[WARNING] Using memory locations instead of labels is not recommended for LMC++ Extended, due to some commands requiring multiple lines.')
    if filename.split('.')[-1] != 'lmcx':
        raise UnsupportedFileTypeError('Unsupported file type {t}'.format(t=filename.split('.')[-1]))
    filename = ''.join(filename.split('.')[:-1])
    # code = load_lmcsym(filename)
    # lmcCode = convert_lmcsym(code)
    # lmcName = write_lmc(name, lmcCode)
    # print('Successfully created {file}'.format(file=lmcName))

if __name__ == '__main__':
    main()