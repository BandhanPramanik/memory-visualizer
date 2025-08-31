import uuid
import os
from flask import Flask, jsonify, request, render_template
from debugger import HelperDebugger

# --- Global Setup ---
app = Flask(__name__)
sessions = {}

# --- NEW: A manifest of your pre-compiled programs ---
# Make sure you've already compiled these:
# gcc -g byteshow.c -o byteshow
# gcc -g test_heap.c -o test_heap
PROGRAMS = {
    "byteshow": {
        "binary_path": "./bin/byteshow",
        "source_path": "./examples/byteshow.c"
    },
    "heap_test": {
        "binary_path": "./bin/test_heap",
        "source_path": "./examples/test_heap.c"
    }
    # Add your other 2-3 programs here
}

# --- Main Route to Serve the Webpage ---
@app.route("/")
def index():
    return render_template("index.html")

# --- API Endpoints ---
@app.route('/start', methods=['POST'])
def start():
    """Starts a new debugging session for a pre-compiled program."""
    program_name = request.get_json().get('program_name')
    if not program_name or program_name not in PROGRAMS:
        return jsonify({"error": "Invalid program selected."}), 400

    # Get the file paths from our manifest
    prog_info = PROGRAMS[program_name]
    binary_path = prog_info["binary_path"]
    source_path = prog_info["source_path"]

    # Read the source code to send to the frontend
    try:
        with open(source_path, 'r') as f:
            source_code_lines = f.readlines()
    except FileNotFoundError:
        return jsonify({"error": f"Source file not found on server: {source_path}"}), 500

    # Create and start the debugger
    session_id = str(uuid.uuid4())
    debugger = HelperDebugger(binary_path, source_path) # Your class needs the source path now
    sessions[session_id] = debugger
    
    initial_state = debugger.start_debugging()
    initial_state['session_id'] = session_id
    # Add the source code to the initial state so the UI can display it
    initial_state['source_code'] = [line.rstrip() for line in source_code_lines]
    
    return jsonify(initial_state)


def command_handler(command):
    """Helper to avoid repeating code in step, run_to_end, etc."""
    session_id = request.get_json().get('session_id')
    if not session_id or session_id not in sessions:
        return jsonify({"error": "Invalid or missing session ID"}), 400
    
    debugger = sessions[session_id]
    
    if command == 'step':
        new_state = debugger.step_over()
    elif command == 'run_to_end':
        new_state = debugger.run_to_end()
    else:
        return jsonify({"error": "Unknown command"}), 400
        
    return jsonify(new_state)
# ... (The rest of your routes: /step, /run_to_end, /stop) ...
# They remain exactly the same.

@app.route('/step', methods=['POST'])
def step_over():
    return command_handler('step')

@app.route('/run_to_end', methods=['POST'])
def run_to_end():
    return command_handler('run_to_end')

@app.route('/stop', methods=['POST'])
def stop():
    """Stops a session and cleans it up."""
    session_id = request.get_json().get('session_id')
    if session_id and session_id in sessions:
        debugger = sessions[session_id]
        debugger.stop_debugging()  # A method in your class to call -gdb-exit
        del sessions[session_id]
    return jsonify({"message": "Session terminated."})

# Note: A "restart" function is just a "stop" followed by a "start",
# which can be handled by your JavaScript.

# --- Boilerplate to Run the App ---
if __name__ == '__main__':
    app.run(debug=True, port=5001)
