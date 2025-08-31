from .coredebugger import Debugger

class HelperDebugger(Debugger):
    def __init__(self, filename, source_file):
        super().__init__(filename)
        self.source_file = source_file


    def _parse_frame_from_response(self, response):
        """
        Finds the 'stopped' message in a GDB response and returns the frame details.
        """
        for msg in response:
            if msg.get('message') == 'stopped':
                # The useful data is right here!
                return msg.get('payload', {}).get('frame', {})
        return None # Return None if the program didn't stop (e.g., it exited)


    def _get_stack_variables(self):
        """
        Calls the 'list-variables' command and parses the response.
        """
        response = self.exec_debug("list-variables")
        # The response is a list, we care about the first message
        if response and response[0].get('message') == 'done':
            return response[0].get('payload', {}).get('variables', [])
        return []


    def _get_heap_data(self, stack_variables):
        """
        Scans stack variables for pointers and reads the memory they point to.
        """
        heap = {}
        for var in stack_variables:
            # A simple way to check for a pointer. 
            value = var.get('value', '')
            if not value.startswith('0x'):
                continue

            address = value.split(' ')[0] # Handles cases like '0x123 "string"'
            # Reading 16 bytes from that address
            mem_response = self.exec_debug("read-memory", (address, "16"))

            if mem_response and mem_response[0].get('message') == 'done':
                # The raw memory data is in a field called 'memory'
                memory_contents = mem_response[0].get('payload', {}).get('memory', [])
                if memory_contents:
                    # The content is a list of dicts with 'addr', 'data', etc.
                    heap[address] = memory_contents[0].get('contents')
        return heap

    # The most important function here
    def _treat_response(self, response):
        # Wait loop
        while not any(msg.get('message') == 'stopped' for msg in response):
            try:
                # ...actively wait for more messages from GDB.
                new_messages = self.gdbmi.get_gdb_response(timeout_sec=5)
                if not new_messages:
                    # If we wait 5s and get nothing, something is wrong.
                    return {"error": "Program did not stop (timeout)."}
                response.extend(new_messages)
            except Exception:
                return {"error": "GDB process ended unexpectedly."}
        # First, check if the program has exited.
        for msg in response:
            if msg.get('message') == 'stopped':
                reason = msg.get('payload', {}).get('reason')
                if reason == 'exited-normally':
                    return {"status": "Done."} # Signal the end

        # To get the line no. and file
        frame = self._parse_frame_from_response(response)
        if not frame:
            return {"error": "Program did not stop at breakpoint."}

        # Now, get the things NOT included in the 'stopped' message, like variables
        variables = self._get_stack_variables()
        heap = self._get_heap_data(variables)

        return {
            "line": frame.get('line'),
            "file": frame.get('file'),
            "frame_name": frame.get('func'),
            "stack": variables,
            "heap": heap,
        }


    def stop_debugging(self):
        self.exec_debug("exit")


    def start_debugging(self):
        """
        Starts the program and stops at the first line of 'main'.
        """
        self.exec_debug("break main")
        response = self.exec_debug("run")
        return self._treat_response(response)


    def step_over(self):
        """
        Executes the current line and moves to the next.
        """
        response = self.exec_debug("next")
        return self._treat_response(response)


    def _find_main_end_line(self):
        """
        A parser to find the line number of the closing brace of main().
        """
        try:
            with open(self.source_file, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return -1
        in_main_scope = False
        found_first_brace = False
        brace_count = 0

        for i, line in enumerate(lines):
            # Only start the process after we find the 'main' function
            if not in_main_scope and "main(" in line:
                in_main_scope = True

            if in_main_scope:
                if '{' in line:
                    brace_count += line.count('{')
                    found_first_brace = True # We are now officially inside a scope

                if '}' in line:
                    brace_count -= line.count('}')

                # If brace_count is 0 AND we have been inside at least one brace,
                # we have found the end of the main function's scope.
                if brace_count == 0 and found_first_brace:
                    return i + 1  # Return line number (1-indexed)

        return -1 # Should not happen in a valid C file

    def run_to_end(self):
        """
        Sets a breakpoint at the end of main and runs the program.
        """
        end_line = self._find_main_end_line()
        if end_line == -1:
            return {"error": "Could not find the end of the main function."}
        self.exec_debug("breakpoint", str(end_line))
        response = self.exec_debug("run")
        return self._treat_response(response)



