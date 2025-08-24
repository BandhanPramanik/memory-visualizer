from pygdbmi.gdbcontroller import GdbController
from pprint import pprint
import shlex


class Debugger:
    def __init__(self, binary):
        self.gdbmi = GdbController()
        self.binary = binary
        print("Started GDB: ", self.gdbmi.command)
        # load the binary automatically
        self.exec_debug("load", binary)

    @staticmethod
    def safe_line(line_str):
        if line_str.isdigit():
            return int(line_str)
        else:
            raise ValueError("Invalid line number")


    def exec_debug(self, command, argg=None):
        command_repo = {
            "load": lambda argg: self.gdbmi.write(f"-file-exec-and-symbols {shlex.quote(argg)}"),
            "breakpoint": lambda argg: self.gdbmi.write(f"-break-insert {self.safe_line(argg)}"),
            "run": lambda argg=None: self.gdbmi.write("-exec-run"),
            "next": lambda argg=None: self.gdbmi.write("-exec-step"),
            "list-frames": lambda argg=None: self.gdbmi.write("-stack-list-frames"),
            "eval": lambda argg: self.gdbmi.write(f"-data-evaluate-expression {shlex.quote(argg)}"),
            "exit": lambda argg=None: self.gdbmi.write("-gdb-exit")
        }
        if command not in command_repo:
            raise ValueError(f"Unknown command: {command}")
        # Load binary a.out and get structured response
        response = command_repo[command](argg)
        pprint(response)
        print("\n-----\n")
        return response



dbg = Debugger("./a.out")
dbg.exec_debug("breakpoint", "9")
dbg.exec_debug("run")
dbg.exec_debug("eval", "lilendian")
dbg.exec_debug("next")
dbg.exec_debug("list-frames")
dbg.exec_debug("exit")


