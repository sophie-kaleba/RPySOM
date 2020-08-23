from rpython.rlib.rbigint import rbigint
from .abstract_object import AbstractObject
from .double          import Double


class BigInteger(AbstractObject):

    _immutable_fields_ = ["_embedded_biginteger"]

    def __init__(self, value):
        AbstractObject.__init__(self)
        assert isinstance(value, rbigint)
        self._embedded_biginteger = value

    def get_embedded_biginteger(self):
        return self._embedded_biginteger

    def get_class(self, universe):
        return universe.integerClass

    def quick_add(self, from_method, frame, interpreter, bytecode_index):
        right = frame.get_stack_element(0)
        frame.pop()
        frame.pop()
        frame.push(self.prim_add(right, interpreter.get_universe()))

    def quick_multiply(self, from_method, frame, interpreter, bytecode_index):
        right = frame.get_stack_element(0)
        frame.pop()
        frame.pop()
        frame.push(self.prim_multiply(right, interpreter.get_universe()))

    def quick_subtract(self, from_method, frame, interpreter, bytecode_index):
        right = frame.get_stack_element(0)
        frame.pop()
        frame.pop()
        frame.push(self.prim_subtract(right, interpreter.get_universe()))

    def _to_double(self, universe):
        return universe.new_double(self._embedded_biginteger.tofloat())

    def prim_less_than(self, right, universe):
        # Check second parameter type:
        if isinstance(right, Double):
            return self._to_double(universe).prim_less_than(right, universe)
        if not isinstance(right, BigInteger):
            result = self._embedded_biginteger.lt(
                rbigint.fromint(right.get_embedded_integer()))
        else:
            result = self._embedded_biginteger.lt(
                right.get_embedded_biginteger())

        if result:
            return universe.trueObject
        else:
            return universe.falseObject

    def prim_as_string(self, universe):
        return universe.new_string(self._embedded_biginteger.str())

    def prim_add(self, right, universe):
        if isinstance(right, BigInteger):
            return universe.new_biginteger(
                right.get_embedded_biginteger().add(self._embedded_biginteger))
        elif isinstance(right, Double):
            return self._to_double(universe).prim_add(right, universe)
        else:
            return universe.new_biginteger(
                rbigint.fromint(right.get_embedded_integer()).add(
                    self._embedded_biginteger))

    def prim_subtract(self, right, universe):
        if isinstance(right, BigInteger):
            r = self._embedded_biginteger.sub(right.get_embedded_biginteger())
        elif isinstance(right, Double):
            return self._to_double(universe).prim_subtract(right, universe)
        else:
            r = self._embedded_biginteger.sub(rbigint.fromint(
                right.get_embedded_integer()))
        return universe.new_biginteger(r)

    def prim_multiply(self, right, universe):
        if isinstance(right, BigInteger):
            r = self._embedded_biginteger.mul(right.get_embedded_biginteger())
        elif isinstance(right, Double):
            return self._to_double(universe).prim_multiply(right, universe)
        else:
            r = self._embedded_biginteger.mul(rbigint.fromint(
                right.get_embedded_integer()))
        return universe.new_biginteger(r)

    def prim_double_div(self, right, universe):
        if isinstance(right, BigInteger):
            r = self._embedded_biginteger.truediv(
                right.get_embedded_biginteger())
        elif isinstance(right, Double):
            return self._to_double(universe).prim_double_div(right, universe)
        else:
            r = self._embedded_biginteger.truediv(rbigint.fromint(
                right.get_embedded_integer()))
        return universe.new_double(r)

    def prim_int_div(self, right, universe):
        if isinstance(right, BigInteger):
            r = self._embedded_biginteger.floordiv(
                right.get_embedded_biginteger())
        elif isinstance(right, Double):
            return self._to_double(universe).prim_int_div(right, universe)
        else:
            r = self._embedded_biginteger.floordiv(rbigint.fromint(
                right.get_embedded_integer()))
        return universe.new_biginteger(r)

    def prim_modulo(self, right, universe):
        if isinstance(right, BigInteger):
            r = self._embedded_biginteger.mod(
                right.get_embedded_biginteger())
        elif isinstance(right, Double):
            return self._to_double(universe).prim_modulo(right, universe)
        else:
            r = self._embedded_biginteger.mod(rbigint.fromint(
                right.get_embedded_integer()))
        return universe.new_biginteger(r)

    def prim_and(self, right, universe):
        if isinstance(right, BigInteger):
            r = self._embedded_biginteger.and_(
                right.get_embedded_biginteger())
        elif isinstance(right, Double):
            return self._to_double(universe).prim_modulo(right, universe)
        else:
            r = self._embedded_biginteger.and_(rbigint.fromint(
                right.get_embedded_integer()))
        return universe.new_biginteger(r)

    def prim_equals(self, right, universe):
        from .integer import Integer
        if isinstance(right, BigInteger):
            result = self._embedded_biginteger.eq(
                right.get_embedded_biginteger())
        elif isinstance(right, Double):
            result = (self._embedded_biginteger.tofloat()
                      == right.get_embedded_double())
        elif isinstance(right, Integer):
            r = right.get_embedded_integer()
            result = self._embedded_biginteger.eq(rbigint.fromint(r))
        else:
            return universe.falseObject

        if result:
            return universe.trueObject
        else:
            return universe.falseObject
