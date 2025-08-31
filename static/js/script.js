let currentSessionId = null;
let currentSourceCode = []; 
const appContainer = document.getElementById('app-container');

// --- Event Listeners ---
// Correctly selects buttons inside the element with CLASS "start-view"
document.querySelectorAll('.start-view button').forEach(btn => {
    btn.addEventListener('click', () => startDebugging(btn.dataset.program));
});

// Correctly selects each control button by its CLASS
document.querySelector('.step-btn').addEventListener('click', () => sendCommand('/step'));
document.querySelector('.run-to-end-btn').addEventListener('click', () => sendCommand('/run_to_end'));
document.querySelector('.stop-btn').addEventListener('click', () => sendCommand('/stop'));
// The "Reset" button will act like a "Stop" button in this design
document.querySelector('.reset-btn').addEventListener('click', () => sendCommand('/stop'));


// --- Core Functions ---
async function startDebugging(programName) {
    const response = await fetch('/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ program_name: programName || 'byteshow' }) // Default to byteshow if no name
    });
    const initialState = await response.json();

    if (initialState.error) {
        alert(`Error: ${initialState.error}`);
        return;
    }
    
    currentSessionId = initialState.session_id;
	currentSourceCode = initialState.source_code;
    appContainer.classList.add('session-active');
    updateUI(initialState);
}

async function sendCommand(endpoint) {
    if (!currentSessionId) return;

    const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: currentSessionId })
    });
    const data = await response.json();

    if (data.error) {
        alert(`Error: ${data.error}`);
    } else if (data.status === "Done." || endpoint === '/stop') {
        alert(data.message || "Execution finished.");
        appContainer.classList.remove('session-active');
        currentSessionId = null;
    } else {
        updateUI(data);
    }
}

// This is the SIMPLER version of updateUI for our single-pane design
function updateUI(state) {
    const codeView = document.querySelector('.debugger-view .font-mono');
    codeView.innerHTML = '';
    
    // THE FIX: Use the saved 'currentSourceCode' instead of 'state.source_code'
    currentSourceCode.forEach((line, index) => {
        const lineSpan = document.createElement('span');
        // GDB line number is 1-indexed, our array is 0-indexed
        if ((index + 1) === parseInt(state.line)) {
            // This is the specific line you highlighted, now fixed
            lineSpan.className = 'bg-yellow-300 text-black px-1';
            lineSpan.textContent = line;
        } else {
            lineSpan.textContent = line;
        }
        codeView.appendChild(lineSpan);
        codeView.appendChild(document.createTextNode('\n')); // Add newline
    });

    // Update the Stack Table
    const stackTable = document.querySelector('.stack-table');
    let stackHtml = '<h4 class="underline">Stack</h4>';
    stackHtml += `<div class="border p-2 rounded bg-white text-black">main()</div>`;
    state.stack.forEach(v => { 
        stackHtml += `<div class="border p-2 rounded bg-white text-black">${v.name} → ${v.value}</div>`; 
    });
    stackTable.innerHTML = stackHtml;
    
    // Update the Heap Table
    const heapTable = document.querySelector('.heap-table');
    let heapHtml = '<h4 class="underline">Heap</h4>';
    for (const address in state.heap) { 
        heapHtml += `<div class="border p-2 rounded bg-white text-black">${address} : ${state.heap[address]}</div>`;
    }
    heapTable.innerHTML = heapHtml;
}
