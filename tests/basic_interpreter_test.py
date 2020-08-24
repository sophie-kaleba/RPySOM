import unittest
import sys
from parameterized import parameterized

from som.compiler.parser import ParseError

from som.vm.universe       import Universe

from som.vmobjects.clazz   import Class
from som.vmobjects.double  import Double
from som.vmobjects.integer import Integer
from som.vmobjects.symbol  import Symbol


class BasicInterpreterTest(unittest.TestCase):
    @parameterized.expand([
        ("MethodCall",     "test",  42, Integer),
        ("MethodCall",     "test2", 42, Integer),

        ("NonLocalReturn", "test",  "NonLocalReturn", Class),
        ("NonLocalReturn", "test1", 42, Integer),
        ("NonLocalReturn", "test2", 43, Integer),
        ("NonLocalReturn", "test3",  3, Integer),
        ("NonLocalReturn", "test4", 42, Integer),
        ("NonLocalReturn", "test5", 22, Integer),

        ("Blocks", "arg1",  42, Integer),
        ("Blocks", "arg2",  77, Integer),
        ("Blocks", "argAndLocal",    8, Integer),
        ("Blocks", "argAndContext",  8, Integer),

        ("Return", "returnSelf",           "Return", Class),
        ("Return", "returnSelfImplicitly", "Return", Class),
        ("Return", "noReturnReturnsSelf",  "Return", Class),
        ("Return", "blockReturnsImplicitlyLastValue", 4, Integer)])
    def test_basic_interpreter_behavior(self, test_class, test_selector,
                                        expected_result, result_type):
        u = Universe()
        u.setup_classpath("Smalltalk:TestSuite/BasicInterpreterTests")

        actual_result = u.execute_method(test_class, test_selector)

        self._assert_equals_SOM_value(expected_result, actual_result,
                                      result_type)

    def _assert_equals_SOM_value(self, expected_result, actual_result,
                                 result_type):
        if result_type is Integer:
            self.assertEquals(expected_result,
                              actual_result.get_embedded_integer())
            return

        if result_type is Double:
            self.assertEquals(expected_result,
                              actual_result.get_embedded_double())
            return

        if result_type is Class:
            self.assertEquals(expected_result,
                              actual_result.get_name().get_embedded_string())
            return

        if result_type is Symbol:
            self.assertEquals(expected_result,
                              actual_result.get_embedded_string())
            return

        self.fail("SOM Value handler missing: " + str(result_type))


if sys.modules.has_key('pytest'):
    # hack to make pytest not to collect the unexpanded test method
    delattr(BasicInterpreterTest, "test_basic_interpreter_behavior")
