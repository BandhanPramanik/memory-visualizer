from pygdbmi.gdbcontroller import GdbController
from pprint import pprint
import shlex

# Globals
filename = "a.out"
command = "xyz"

def safe_line(line_str):
    if line_str.isdigit():
        return int(line_str)
    else:
        raise ValueError("Invalid line number")

def exec_debug(command):
    command_repo = {
        "load": lambda f: gdbmi.write(f"-file-exec-file {shlex.quote(f)}"),
        "breakpoint": lambda line: gdbmi.write(f"-break-insert {safe_line(line)}"),
        "run": lambda: gdbmi.write("-exec-run"),
        "next": lambda: gdbmi.write("-exec-step"),
        "list-frames": lambda: gdbmi.write("-stack-list-frames"),
        "eval": lambda expr: gdbmi.write(f"-data-evaluate-expression {shlex.quote(expr)}"),
        "exit": lambda: gdbmi.write("-gdb-exit")
    }


    # Start gdb process
    gdbmi = GdbController()
    print(gdbmi.get_subprocess_cmd())  # print actual command run as subprocess

    # Load binary a.out and get structured response
    response = ;
    pprint(response)





