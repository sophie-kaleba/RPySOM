class AbstractObject(object):

    def __init__(self):
        pass

    def send(self, frame, selector_string, arguments, universe, interpreter):
        # Turn the selector string into a selector
        selector = universe.symbol_for(selector_string)

        # Push the receiver onto the stack
        frame.push(self)

        # Push the arguments onto the stack
        for arg in arguments:
            frame.push(arg)

        # Lookup the invokable
        invokable = self.get_class(universe).lookup_invokable(selector)

        # Invoke the invokable
        invokable.invoke(frame, interpreter)

    def send_does_not_understand(self, frame, selector, interpreter):
        universe = interpreter.get_universe()

        # Compute the number of arguments
        number_of_arguments = selector.get_number_of_signature_arguments() - 1  ## do ignore self

        # Allocate an array with enough room to hold all arguments
        arguments_array = universe.new_array_with_length(number_of_arguments)

        # Remove all arguments and put them in the freshly allocated array
        i = number_of_arguments - 1

        while i >= 0:
            arguments_array.set_indexable_field(i, frame.pop())
            i -= 1

        frame.pop()  # pop self from stack
        args = [selector, arguments_array]
        self.send(frame, "doesNotUnderstand:arguments:", args, universe, interpreter)

    def send_unknown_global(self, frame, global_name, universe, interpreter):
        arguments = [global_name]
        self.send(frame, "unknownGlobal:", arguments, universe, interpreter)

    def send_escaped_block(self, frame, block, universe, interpreter):
        arguments = [block]
        self.send(frame, "escapedBlock:", arguments, universe, interpreter)

    def get_class(self, universe):
        raise NotImplementedError("Subclasses need to implement get_class(universe).")

    def quick_add(self, from_method, frame, interpreter, bytecode_index):
        interpreter._send(from_method, frame, interpreter._add_symbol,
                          self.get_class(interpreter.get_universe()),
                          bytecode_index)

    def quick_multiply(self, from_method, frame, interpreter, bytecode_index):
        interpreter._send(from_method, frame, interpreter._multiply_symbol,
                          self.get_class(interpreter.get_universe()),
                          bytecode_index)

    def quick_subtract(self, from_method, frame, interpreter, bytecode_index):
        interpreter._send(from_method, frame, interpreter._subtract_symbol,
                          self.get_class(interpreter.get_universe()),
                          bytecode_index)

    @staticmethod
    def is_invokable():
        return False

    def __str__(self):
        from som.vm.universe import get_current
        return "a " + self.get_class(get_current()).get_name().get_string()
