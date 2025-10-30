// DOM elements
const jobCountInput = document.getElementById('jobCount');
const confirmJobsBtn = document.getElementById('confirmJobs');
const uploadSection = document.getElementById('uploadSection');
const uploadBtn = document.getElementById('uploadBtn');
const jobFilesInput = document.getElementById('jobFiles');
const profitSection = document.getElementById('profitSection');
const profitInputsDiv = document.getElementById('profitInputs');
const dependencySection = document.getElementById('dependencySection');
const dependencyInputsDiv = document.getElementById('dependencyInputs');
const deadlineSection = document.getElementById('deadlineSection');
const submitSection = document.getElementById('submitSection');
const submitBtn = document.getElementById('submitBtn');
const resultSection = document.getElementById('resultSection');
const resultText = document.getElementById('resultText');

let jobCount = 0;
let uploadedFiles = [];

// Step 1: Confirm number of jobs
confirmJobsBtn.addEventListener('click', () => {
    jobCount = parseInt(jobCountInput.value);
    if (isNaN(jobCount) || jobCount <= 0) {
        alert("Please enter a valid number of jobs.");
        return;
    }
    uploadSection.style.display = 'block';
});

// Step 2: Handle file uploads
uploadBtn.addEventListener('click', () => {
    const files = Array.from(jobFilesInput.files);
    if (files.length !== jobCount) {
        alert(`You must upload exactly ${jobCount} job files.`);
        return;
    }

    uploadedFiles = files.map(file => file.name.replace(".py", ""));
    alert("Files uploaded successfully!");
    uploadSection.style.display = 'none';
    showProfitInputs();
});

// Step 3: Ask for profit for each job
function showProfitInputs() {
    profitInputsDiv.innerHTML = '';
    uploadedFiles.forEach(job => {
        const div = document.createElement('div');
        div.innerHTML = `
            <label>Profit for ${job}:</label>
            <input type="number" id="profit-${job}" placeholder="Enter profit">
        `;
        profitInputsDiv.appendChild(div);
    });
    profitSection.style.display = 'block';
    showDependencyInputs();
}

// Step 4: Ask dependencies for each job
function showDependencyInputs() {
    dependencyInputsDiv.innerHTML = '';
    uploadedFiles.forEach(job => {
        const div = document.createElement('div');
        const otherJobs = uploadedFiles.filter(j => j !== job);
        const options = otherJobs.map(j => `<option value="${j}">${j}</option>`).join('');

        div.innerHTML = `
            <label>Dependencies for ${job} (if any):</label>
            <select id="dep-${job}" multiple>
                ${options}
            </select>
        `;
        dependencyInputsDiv.appendChild(div);
    });
    dependencySection.style.display = 'block';
    deadlineSection.style.display = 'block';
    submitSection.style.display = 'block';
}

// Step 5: Handle final submission
submitBtn.addEventListener('click', async () => {
    const profits = {};
    const dependencies = {};

    for (let job of uploadedFiles) {
        const profitValue = parseInt(document.getElementById(`profit-${job}`).value);
        if (isNaN(profitValue) || profitValue < 0) {
            alert(`Please enter a valid profit for ${job}.`);
            return;
        }
        profits[job] = profitValue;

        const selectedDeps = Array.from(document.getElementById(`dep-${job}`).selectedOptions).map(opt => opt.value);
        dependencies[job] = selectedDeps;
    }

    const deadline = parseInt(document.getElementById('deadline').value);
    if (isNaN(deadline) || deadline <= 0) {
        alert("Please enter a valid deadline.");
        return;
    }

    const formData = new FormData();
    Array.from(jobFilesInput.files).forEach(file => formData.append('files', file));
    formData.append('profits', JSON.stringify(profits));
    formData.append('dependencies', JSON.stringify(dependencies));
    formData.append('deadline', deadline);

    try {
        const response = await fetch('http://127.0.0.1:5000/run_scheduler', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        resultSection.style.display = 'block';
        resultText.innerText = `✅ Optimal Job Order: ${data.order.join(', ')}
💰 Total Profit: ${data.total_profit}
⏱️ Total Time Used: ${data.total_time}s`;
    } catch (err) {
        alert("Error connecting to backend. Make sure Flask server is running.");
        console.error(err);
    }
});
