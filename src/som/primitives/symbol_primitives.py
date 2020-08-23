from som.primitives.primitives import Primitives
from som.vmobjects.primitive   import Primitive


def _asString(ivkbl, frame, interpreter):
    rcvr = frame.pop()
    frame.push(interpreter.get_universe().new_string(rcvr.get_embedded_string()))


def _equals(ivkbl, frame, interpreter):
    op1 = frame.pop()
    op2 = frame.pop()  # rcvr
    universe = interpreter.get_universe()
    if op1 == op2:
        frame.push(universe.trueObject)
    else:
        frame.push(universe.falseObject)


class SymbolPrimitives(Primitives):

    def install_primitives(self):
        self._install_instance_primitive(Primitive("asString", self._universe,
                                                   _asString))
        self._install_instance_primitive(Primitive("=", self._universe, _equals))
