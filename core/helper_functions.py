__author__ = 'gulliver - Radek Simkanic - SIM0094'


def isIterable(obj):
    try: iter(obj)
    except: return False
    return True

def toInlineList(matrix):
    inline_list = []

    for item in matrix:
        if isIterable(item):
            list = toInlineList(item)
            for add in list:
                inline_list.append(add)
        else:
            inline_list.append(item)

    #return itertools.chain.from_iterable(matrix)
    return inline_list

def counter(data, find, list):
    count = 0
    for item in toInlineList(list):
        if item == find:
            count += 1
    print count

def readBlocks(file_obj, size):
    while True:
        data = file_obj.read(size)
        if not data:
            break
        yield data
