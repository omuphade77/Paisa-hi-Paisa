let uploadedFiles = [];
let graph = {};
let usedDeps = new Set();

// Step 1 — Confirm number of jobs
document.getElementById("confirmJobs").addEventListener("click", () => {
    const jobCount = parseInt(document.getElementById("jobCount").value);
    if (isNaN(jobCount) || jobCount <= 0) {
        alert("Please enter a valid number of jobs.");
        return;
    }
    document.getElementById("uploadSection").style.display = "block";
});

// Step 2 — Handle file upload
document.getElementById("uploadBtn").addEventListener("click", () => {
    const files = Array.from(document.getElementById("jobFiles").files);
    if (files.length === 0) {
        alert("Please upload at least one Python file.");
        return;
    }
    uploadedFiles = files;
    generateProfitInputs(files);
});

// Step 3 — Profit inputs
function generateProfitInputs(files) {
    const container = document.getElementById("profitInputs");
    container.innerHTML = "";
    files.forEach((file) => {
        const div = document.createElement("div");
        div.innerHTML = `
            <label>Profit for ${file.name}:</label>
            <input type="number" class="profitInput" data-filename="${file.name}" placeholder="Enter profit">
        `;
        container.appendChild(div);
    });
    document.getElementById("profitSection").style.display = "block";
    document.getElementById("dependencySection").style.display = "block";
    generateDependencyInputs(files);
}

// Step 4 — Dependency dropdowns
function generateDependencyInputs(files) {
    const container = document.getElementById("dependencyInputs");
    container.innerHTML = "";

    files.forEach((file) => {
        graph[file.name] = [];
        const div = document.createElement("div");

        const select = document.createElement("select");
        select.multiple = true;
        select.dataset.filename = file.name;

        files.forEach((f) => {
            if (f.name !== file.name) {
                const opt = document.createElement("option");
                opt.value = f.name;
                opt.textContent = f.name;
                select.appendChild(opt);
            }
        });

        select.addEventListener("change", (e) => handleDependencyChange(e, files));

        div.innerHTML = `<label>Select dependencies for ${file.name}:</label>`;
        div.appendChild(select);
        container.appendChild(div);
    });

    document.getElementById("deadlineSection").style.display = "block";
    document.getElementById("submitSection").style.display = "block";
}

// Step 5 — Handle dependency selection
function handleDependencyChange(e, files) {
    const job = e.target.dataset.filename;
    const selected = Array.from(e.target.selectedOptions).map((opt) => opt.value);

    // Test if adding new deps would create a cycle
    for (let dep of selected) {
        graph[job].push(dep);
        if (detectCycle(graph)) {
            alert(`❌ Adding ${dep} creates a cycle!`);
            graph[job].pop(); // revert
            e.target.value = "";
            return;
        }
        graph[job].pop();
    }

    // Safe update
    graph[job] = selected;

    // Update shared dependencies
    usedDeps.clear();
    for (let deps of Object.values(graph)) {
        deps.forEach((d) => usedDeps.add(d));
    }

    // Disable already used deps globally
    document.querySelectorAll("select").forEach((sel) => {
        Array.from(sel.options).forEach((opt) => {
            if (
                usedDeps.has(opt.value) &&
                !graph[sel.dataset.filename].includes(opt.value)
            ) {
                opt.disabled = true;
            } else {
                opt.disabled = false;
            }
        });
    });
}

// --- DFS Cycle detection ---
function detectCycle(graph) {
    const visited = new Set();
    const stack = new Set();

    function dfs(node) {
        if (!graph[node]) return false;
        if (stack.has(node)) return true;
        if (visited.has(node)) return false;

        visited.add(node);
        stack.add(node);

        for (let neighbor of graph[node]) {
            if (dfs(neighbor)) return true;
        }

        stack.delete(node);
        return false;
    }

    for (let node in graph) {
        if (dfs(node)) return true;
    }
    return false;
}

// Step 6 — Submit all data
document.getElementById("submitBtn").addEventListener("click", async () => {
    const profits = {};
    document.querySelectorAll(".profitInput").forEach((input) => {
        profits[input.dataset.filename] = parseFloat(input.value) || 0;
    });

    const deadline = parseFloat(document.getElementById("deadline").value);
    if (isNaN(deadline) || deadline <= 0) {
        alert("Please enter a valid deadline.");
        return;
    }

    // Prepare payload
    const formData = new FormData();
    uploadedFiles.forEach((file) => formData.append("files", file));
    formData.append("profits", JSON.stringify(profits));
    formData.append("dependencies", JSON.stringify(graph));
    formData.append("deadline", deadline);

    // Send to backend
    try {
        const response = await fetch("http://127.0.0.1:8000/process_jobs", {
            method: "POST",
            body: formData,
        });
        const result = await response.json();
        document.getElementById("resultSection").style.display = "block";
        document.getElementById("resultText").innerText = result.message;
    } catch (err) {
        alert("Error submitting data: " + err);
    }
});
