from rpython.rlib.rarithmetic import ovfcheck, LONG_BIT
from rpython.rlib.rbigint import rbigint
from som.primitives.primitives import Primitives
from som.vmobjects.integer import Integer
from som.vmobjects.primitive   import Primitive
from som.vmobjects.double      import Double
from som.vmobjects.string      import String
from som.vmobjects.block       import block_evaluate

import math


def _asString(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(rcvr.prim_as_string(interpreter.get_universe()))


def _sqrt(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    res = math.sqrt(rcvr.get_embedded_integer())
    if res == float(int(res)):
        frame.push(interpreter.get_universe().new_integer(int(res)))
    else:
        frame.push(interpreter.get_universe().new_double(res))


def _atRandom(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_integer(int(
        rcvr.get_embedded_integer() * interpreter.get_universe().random.random())))


def _plus(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()
    frame.push(left.prim_add(right_obj, interpreter.get_universe()))


def _minus(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()
    frame.push(left.prim_subtract(right_obj, interpreter.get_universe()))


def _mult(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()
    frame.push(left.prim_multiply(right_obj, interpreter.get_universe()))


def _doubleDiv(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()
    frame.push(left.prim_double_div(right_obj, interpreter.get_universe()))


def _intDiv(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()
    frame.push(left.prim_int_div(right_obj, interpreter.get_universe()))


def _mod(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()
    frame.push(left.prim_modulo(right_obj, interpreter.get_universe()))


def _and(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()
    frame.push(left.prim_and(right_obj, interpreter.get_universe()))


def _equals(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()
    frame.push(left.prim_equals(right_obj, interpreter.get_universe()))


def _lessThan(ivkbl, frame, interpreter):
    right_obj = frame.pop()
    left      = frame.pop()
    frame.push(left.prim_less_than(right_obj, interpreter.get_universe()))


def _fromString(ivkbl, frame, interpreter):
    param = frame.pop()
    frame.pop()

    if not isinstance(param, String):
        frame.push(interpreter.get_universe().nilObject)
        return

    int_value = int(param.get_embedded_string())
    frame.push(interpreter.get_universe().new_integer(int_value))


def _leftShift(ivkbl, frame, interpreter):
    right = frame.pop()
    left  = frame.pop()
    universe  = interpreter.get_universe()
    assert isinstance(right, Integer)

    l = left.get_embedded_integer()
    r = right.get_embedded_integer()
    try:
        if not (l == 0 or 0 <= r < LONG_BIT):
            raise OverflowError
        result = ovfcheck(l << r)
        frame.push(universe.new_integer(result))
    except OverflowError:
        frame.push(universe.new_biginteger(
            rbigint.fromint(l).lshift(r)))


def _bitXor(ivkbl, frame, interpreter):
    right = frame.pop()
    left  = frame.pop()

    result = left.get_embedded_integer() ^ right.get_embedded_integer()

    frame.push(interpreter.get_universe().new_integer(result))


from rpython.rlib import jit


def get_printable_location(interpreter, block_method):
    from som.vmobjects.method import Method
    assert isinstance(block_method, Method)
    return "to:do: [%s>>%s]" % (block_method.get_holder().get_name().get_embedded_string(),
                                block_method.get_signature().get_embedded_string())


jitdriver_int = jit.JitDriver(
    greens=['interpreter', 'block_method'],
    reds='auto',
    # virtualizables=['frame'],
    get_printable_location=get_printable_location)

jitdriver_double = jit.JitDriver(
    greens=['interpreter', 'block_method'],
    reds='auto',
    # virtualizables=['frame'],
    get_printable_location=get_printable_location)


def _toDoInt(i, top, frame, context, interpreter, block_method, universe):
    assert isinstance(i, int)
    assert isinstance(top, int)
    while i <= top:
        jitdriver_int.jit_merge_point(interpreter=interpreter,
                                      block_method=block_method)

        b = universe.new_block(block_method, context)
        frame.push(b)
        frame.push(universe.new_integer(i))
        block_evaluate(b, interpreter, frame)
        frame.pop()
        i += 1


def _toDoDouble(i, top, frame, context, interpreter, block_method, universe):
    assert isinstance(i, int)
    assert isinstance(top, float)
    while i <= top:
        jitdriver_double.jit_merge_point(interpreter=interpreter,
                                         block_method=block_method)

        b = universe.new_block(block_method, context)
        frame.push(b)
        frame.push(universe.new_integer(i))
        block_evaluate(b, interpreter, frame)
        frame.pop()
        i += 1


def _toDo(ivkbl, frame, interpreter):
    universe = interpreter.get_universe()
    block = frame.pop()
    limit = frame.pop()
    self  = frame.pop()  # we do leave it on there

    block_method = block.get_method()
    context      = block.get_context()

    i = self.get_embedded_integer()
    if isinstance(limit, Double):
        _toDoDouble(i, limit.get_embedded_double(), frame, context, interpreter,
                    block_method, universe)
    else:
        _toDoInt(i, limit.get_embedded_integer(), frame, context, interpreter,
                 block_method, universe)

    frame.push(self)


class IntegerPrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(Primitive("asString", self._universe, _asString))
        self._install_instance_primitive(Primitive("sqrt",     self._universe, _sqrt))
        self._install_instance_primitive(Primitive("atRandom", self._universe, _atRandom))

        self._install_instance_primitive(Primitive("+",  self._universe, _plus))
        self._install_instance_primitive(Primitive("-",  self._universe, _minus))

        self._install_instance_primitive(Primitive("*",  self._universe, _mult))
        self._install_instance_primitive(Primitive("//", self._universe, _doubleDiv))
        self._install_instance_primitive(Primitive("/",  self._universe, _intDiv))
        self._install_instance_primitive(Primitive("%",  self._universe, _mod))
        self._install_instance_primitive(Primitive("&",  self._universe, _and))
        self._install_instance_primitive(Primitive("=",  self._universe, _equals))
        self._install_instance_primitive(Primitive("<",  self._universe, _lessThan))

        self._install_instance_primitive(Primitive("<<", self._universe, _leftShift))
        self._install_instance_primitive(Primitive("bitXor:", self._universe, _bitXor))

        self._install_instance_primitive(Primitive("to:do:", self._universe, _toDo))

        self._install_class_primitive(Primitive("fromString:", self._universe, _fromString))
