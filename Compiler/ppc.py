import util
import math

from Compiler.types import Array, sint, sfloat, sfix, MemValue, cint, Matrix, _int
# import operator
# import math
# from Compiler.instructions import *
from Compiler.library import for_range, print_str, for_range, print_float_prec
import ml


pint = sint
pfloat = sfloat
pfix = sfix
pnum = pfloat

print_float_prec(4)

# Use to limit the tester workload
MAX_DATA_LENGTH = 500
MAX_ML_SIZE = 500

ppcConv2d = ml.FixConv2d
ppcMaxPool = ml.MaxPool
ppcRelu = ml.Relu
ppcDense = ml.Dense

def set_display_field_names(name_list):
    println("result_fields = %s", ' '.join(name_list))


def display_data(field_values):
    printfmt("result_values =")
    for value in field_values:
        printfmt(" %s", value)
    println()


def get_ml_size(shape_array):
    ml_size = 1
    for i in range(1, len(shape_array)):
        ml_size *= shape_array[i]
    return ml_size


def pConv2d(input_shape, weight_shape, bias_shape, output_shape, stride,
            padding='SAME', tf_weight_format=False, inputs=None):
    input_shape_size = get_ml_size(input_shape)
    if input_shape_size > MAX_ML_SIZE:
        raise TypeError('input_shape could not larger than %s', MAX_ML_SIZE)
    bias_shape_size = get_ml_size(bias_shape)
    if bias_shape_size > MAX_ML_SIZE:
        raise TypeError('bias_shape could not larger than %s', MAX_ML_SIZE)
    return ml.FixConv2d(input_shape, weight_shape, bias_shape, output_shape, stride,
                        padding, tf_weight_format=False, inputs=None)


def pMaxPool(shape, strides=(1, 2, 2, 1), ksize=(1, 2, 2, 1),
             padding='VALID'):
    shape_size = get_ml_size(shape)
    if shape_size > MAX_ML_SIZE:
        raise TypeError('shape could not larger than %s', MAX_ML_SIZE)
    strides_size = get_ml_size(strides)
    if strides_size > MAX_ML_SIZE:
        raise TypeError('strides_size could not larger than %s', MAX_ML_SIZE)
    ksize_size = get_ml_size(ksize)
    if ksize_size > MAX_ML_SIZE:
        raise TypeError('ksize_size could not larger than %s', MAX_ML_SIZE)
    return ml.MaxPool(shape, strides, ksize,
                      padding)


def pRelu(shape, inputs=None):
    shape_size = get_ml_size(shape)
    if shape_size > MAX_ML_SIZE:
        raise TypeError('shape could not larger than %s', MAX_ML_SIZE)
    return ml.Relu(shape, inputs)


def pDense(N, d_in, d_out, d=1, activation='id', debug=False):
    if d_out > MAX_ML_SIZE:
        raise TypeError('d_out could not larger than %s', MAX_ML_SIZE)
    return ml.Dense(N, d_in, d_out, d, activation, debug)


def read_array(party_id, source_record_count, value_type=pnum):
    if source_record_count > MAX_DATA_LENGTH:
        raise TypeError(
            'Array length could not larger than %s', MAX_DATA_LENGTH)
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
        raise TypeError('Matrix size could not larger than %s',
                        MAX_DATA_LENGTH)
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


def to_pint(num):
    if isinstance(num, pint):
        return num

    if isinstance(num, pfloat):
        num = pfix(num)

    if isinstance(num, pfix):
        return num.v >> pfix.f

    raise NotImplementedError('to_pint only implemented for pfloat and pfix.')


def pint_mod(self, other):
    if isinstance(other, int):
        l = math.log(other, 2)
        if 2**int(round(l)) == other:
            return self.mod2m(int(l))
        else:
            return self - to_pint(pfix(self) / other) * other

    if isinstance(other, _int):
        return self - to_pint(pfix(self) / other) * other

    raise NotImplementedError('Argument modulus should be an integer type.')


def pint_div(self, other):
    if isinstance(other, int):
        l = math.log(other, 2)
        if 2**int(round(l)) == other:
            println("%s, %s, %s", (self >> l).reveal(), self.reveal(), l)
            return self >> l
        else:
            return pfix(self) / other

    # pfloat sometime produces buggy results, has to use pfix here.
    if isinstance(other, _int):
        return pfix(self) / other

    raise NotImplementedError(
        'Argument denominator should be an integer type.')


def pint_truediv(self, other):
    return pnum(pint_div(self, other))


def pint_floordiv(self, other):
    return to_pint(pint_div(self, other))


pint.__mod__ = pint_mod
#pint.__truediv__ = pint_truediv
pint.__floordiv__ = pint_floordiv
