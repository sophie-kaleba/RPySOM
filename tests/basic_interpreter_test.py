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
        # ("Self", "testAssignSuper", 42, ParseError),
        # ("Self", "testAssignSelf", 42, ParseError),

        ("MethodCall", "test", 42, Integer),
        ("MethodCall", "test2", 42, Integer),

        ("NonLocalReturn", "test1", 42, Integer),
        ("NonLocalReturn", "test2", 43, Integer),
        ("NonLocalReturn", "test3", 3, Integer),
        ("NonLocalReturn", "test4", 42, Integer),
        ("NonLocalReturn", "test5", 22, Integer),

        ("Blocks", "testArg1", 42, Integer),
        ("Blocks", "testArg2", 77, Integer),
        ("Blocks", "testArgAndLocal", 8, Integer),
        ("Blocks", "testArgAndContext", 8, Integer),

        ("Return", "testReturnSelf", "Return", Class),
        ("Return", "testReturnSelfImplicitly", "Return", Class),
        ("Return", "testNoReturnReturnsSelf", "Return", Class),
        ("Return", "testBlockReturnsImplicitlyLastValue", 4, Integer),

        ("IfTrueIfFalse", "test", 42, Integer),
        ("IfTrueIfFalse", "test2", 33, Integer),
        ("IfTrueIfFalse", "test3", 4, Integer),

        ("CompilerSimplification", "testReturnConstantSymbol", "constant", Symbol),
        ("CompilerSimplification", "testReturnConstantInt", 42, Integer),
        ("CompilerSimplification", "testReturnSelf", "CompilerSimplification", Class),
        ("CompilerSimplification", "testReturnSelfImplicitly", "CompilerSimplification", Class),
        ("CompilerSimplification", "testReturnArgumentN", 55, Integer),
        ("CompilerSimplification", "testReturnArgumentA", 44, Integer),
        ("CompilerSimplification", "testSetField", "foo", Symbol),
        ("CompilerSimplification", "testGetField", 40, Integer),

        ("Hash", "testHash", 444, Integer),

        ("Arrays", "testEmptyToInts", 3, Integer),
        ("Arrays", "testPutAllInt", 5, Integer),
        ("Arrays", "testPutAllNil", "Nil", Class),
        ("Arrays", "testPutAllBlock", 3, Integer),
        ("Arrays", "testNewWithAll", 1, Integer),

        ("BlockInlining", "testNoInlining", 1, Integer),
        ("BlockInlining", "testOneLevelInlining", 1, Integer),
        ("BlockInlining", "testOneLevelInliningWithLocalShadowTrue", 2, Integer),
        ("BlockInlining", "testOneLevelInliningWithLocalShadowFalse", 1, Integer),

        ("BlockInlining", "testBlockNestedInIfTrue", 2, Integer),
        ("BlockInlining", "testBlockNestedInIfFalse", 42, Integer),

        ("BlockInlining", "testDeepNestedInlinedIfTrue", 3, Integer),
        ("BlockInlining", "testDeepNestedInlinedIfFalse", 42, Integer),

        ("BlockInlining", "testDeepNestedBlocksInInlinedIfTrue", 5, Integer),
        ("BlockInlining", "testDeepNestedBlocksInInlinedIfFalse", 43, Integer),

        ("BlockInlining", "testDeepDeepNestedTrue", 9, Integer),
        ("BlockInlining", "testDeepDeepNestedFalse", 43, Integer),

        ("BlockInlining", "testToDoNestDoNestIfTrue", 2, Integer),

        ("NonLocalVars", "testWriteDifferentTypes", 3.75, Double),

        ("ObjectCreation", "test", 1000000, Integer),

        ("Regressions", "testSymbolEquality", 1, Integer),
        ("Regressions", "testSymbolReferenceEquality", 1, Integer),
        ("Regressions", "testUninitializedLocal", 1, Integer),
        ("Regressions", "testUninitializedLocalInBlock", 1, Integer),

        ("BinaryOperation", "test", 3 + 8, Integer),

        ("NumberOfTests", "numberOfTests", 52, Integer)])
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
