import util
from Compiler.types import Array, sint, sfloat
# import operator
# import math
# from Compiler.instructions import *
from Compiler.library import for_range_opt, print_str

class pint(sint):
    pass


def condition(cond, a, b):
    return util.if_else(cond, a, b)


def read_int_data(party_id, source_record_count):
    array_value = Array(source_record_count, sint)
    @for_range_opt(source_record_count)
    def _(i):
        array_value[i] = sint.get_input_from(party_id)
    return array_value

def read_float_data(party_id, source_record_count):
    array_value = Array(source_record_count, sfloat)
    @for_range_opt(source_record_count)
    def _(i):
        array_value[i] = sfloat.get_input_from(party_id)
    return array_value

def get_float_result(source_record_count):
    return Array(source_record_count, sfloat)

def println(s='', *args):
    print_str(s + '\n', *args)

# def max_array(int_record_array, array_count):

