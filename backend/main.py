from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile, os, json
from typing import List

from .logic import validate_and_extract_chains, build_prefixes, knapsack
from .utils import measure_runtime


app = FastAPI(title="Job Scheduler Backend")

@app.post("/process_jobs")
async def process_jobs(
    files: List[UploadFile] = File(...),
    profits: str = Form(...),
    dependencies: str = Form(...),
    deadline: float = Form(...)
):
    # parse user inputs
    try:
        profits = json.loads(profits)
        dependencies = json.loads(dependencies)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format.")

    tmpdir = tempfile.mkdtemp(prefix="jobs_")
    job_info = {}

    # save files + measure runtime
    for file in files:
        filepath = os.path.join(tmpdir, file.filename)
        with open(filepath, "wb") as f:
            f.write(await file.read())

        try:
            runtime = measure_runtime(filepath)
        except RuntimeError as e:
            raise HTTPException(status_code=400, detail=str(e))

        job_info[file.filename] = {"runtime": runtime, "profit": profits[file.filename]}

    jobs = list(job_info.keys())

    try:
        chains = validate_and_extract_chains(jobs, dependencies)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    prefixes = build_prefixes(chains, job_info)
    capacity = int(deadline * 1000)  # convert seconds → ms
    max_profit, used_time, sequence = knapsack(prefixes, capacity)

    return JSONResponse({
        "max_profit": max_profit,
        "used_time_ms": used_time,
        "sequence": sequence,
        "chains": chains,
        "job_info": job_info
    })
