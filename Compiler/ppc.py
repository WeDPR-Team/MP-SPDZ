import util
from Compiler.types import Array, sint, sfloat, sfix,MemValue, cint, Matrix
# import operator
# import math
# from Compiler.instructions import *
from Compiler.library import for_range, print_str, for_range

pint = sint
pfloat = sfloat
pfix = sfix
pnum = pfloat

# Use to limit the tester workload
MAX_DATA_LENGTH = 500

def read_array(party_id, source_record_count, value_type=pnum):
    if source_record_count > MAX_DATA_LENGTH:
        raise TypeError('Array length could not larger than %s', MAX_DATA_LENGTH)
    array_value = Array(source_record_count, value_type)
    array_value.input_from(party_id)
    return array_value


def max_in_array(array):
    max_value = MemValue(array[0])
    max_index = MemValue(pint(0))

    @for_range(1, array.length)
    def _(i):
        cond = array[i] > max_value
        max_index.write(condition(cond, pint(i), max_index.read()))
        max_value.write(condition(cond, array[i], max_value.read()))
    return max_value.read(), max_index.read()

def min_in_array(array):
    value = MemValue(array[0])
    index = MemValue(pint(0))

    @for_range(1, array.length)
    def _(i):
        cond = array[i] < value
        index.write(condition(cond, pint(i), index.read()))
        value.write(condition(cond, array[i], value.read()))
    return value.read(), index.read()

def combine_array(array1, array2):
    if array1.value_type != array2.value_type:
        raise TypeError('Array type does not match')
    result_array = Array(array1.length+array2.length, array1.value_type)
    result_array.assign(array1)
    result_array.assign(array2, array1.length)
    return result_array

def print_array(array):
    printfmt("[ ")
    @for_range(array.length)
    def _(i):
        printfmt("%s ", array[i].reveal())
    println("]")


def read_matrix(party_id, height, width, value_type=pnum):
    if height*width > MAX_DATA_LENGTH:
        raise TypeError('Matrix size could not larger than %s', MAX_DATA_LENGTH)
    value = Matrix(height, width, value_type)
    value.input_from(party_id)
    return value


def print_matrix(matrix):
    println("[")
    @for_range(matrix.sizes[0])
    def _(i):
        printfmt(" [ ")
        @for_range(matrix.sizes[1])
        def _(j):
            printfmt("%s ", matrix[i][j].reveal())
        println("]")
    println("]")


def condition(cond, a, b):
    return util.if_else(cond, a, b)

def println(s='', *args):
    print_str(s + '\n', *args)

def printfmt(s='', *args):
    print_str(s, *args)
