
def common_prefix(strings):
    if len(strings) == 0:
        print('simple_utilities.py: common_prefix(strings): Error: Bad input. Not a list of strings?')

    if len(strings) == 1:
        return strings[0]

    accumulator = ''
    k=min([len(s) for s in strings])
    while True:
        next_char = strings[0][len(accumulator)]
        for string in strings:
            if next_char != string[len(accumulator)]:
                return accumulator
        accumulator += next_char
        if k == len(accumulator):
            return accumulator
