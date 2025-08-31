from pygdbmi.gdbcontroller import GdbController
import shlex


class Debugger:
    def __init__(self, binary):
        self.gdbmi = GdbController()
        self.binary = binary
        print("Started GDB: ", self.gdbmi.command)
        # load the binary automatically
        self.exec_debug("load", binary)

    @staticmethod
    def safe_num(line_str):
        if line_str.isdigit():
            return int(line_str)
        else:
            raise ValueError("Invalid line number")


    def exec_debug(self, command, argg=None):
        command_repo = {
            "break main": lambda argg=None: self.gdbmi.write("b main"),
            "breakpoint": lambda argg: self.gdbmi.write(f"-break-insert {self.safe_num(argg)}"),
            "eval": lambda argg: self.gdbmi.write(f"-data-evaluate-expression {shlex.quote(argg)}"),
            "exit": lambda argg=None: self.gdbmi.write("-gdb-exit", read_response=False),
            "load": lambda argg: self.gdbmi.write(f"-file-exec-and-symbols {shlex.quote(argg)}"),
            "list-frames": lambda argg=None: self.gdbmi.write("-stack-list-frames"),
            "list-variables": lambda argg=None: self.gdbmi.write("-stack-list-variables --all-values"),
            "next": lambda argg=None: self.gdbmi.write("-exec-step"),
            "read-memory": lambda argg: self.gdbmi.write(f"-data-read-memory-bytes {shlex.quote(argg[0])} {self.safe_num(argg[1])}"),
            "run": lambda argg=None: self.gdbmi.write("-exec-run"),
            "set-tty": lambda argg: self.gdbmi.write(f'set inferior-tty {argg}')
        }
        if command not in command_repo:
            raise ValueError(f"Unknown command: {command}")
        # Load binary a.out and get structured response
        response = command_repo[command](argg)
        return response




