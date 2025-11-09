from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile, os, json, shutil
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware
from .logic import validate_and_extract_chains, build_prefixes, knapsack
from .utils import measure_runtime
import uvicorn

app = FastAPI(title="Job Scheduler Backend")

# Allow frontend access (dev). For production restrict origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
async def ping():
    return {"message": "pong"}


@app.post("/process_jobs")
async def process_jobs(
    files: List[UploadFile] = File(...),
    profits: str = Form(...),
    dependencies: str = Form(...),
    deadline: float = Form(...)
):
    """
    Expects:
      - files: uploaded .py files (list)
      - profits: JSON string mapping filename -> profit
      - dependencies: JSON string mapping filename -> [filenames]
      - deadline: numeric seconds
    """
    # parse JSON form fields
    try:
        profits_map: Dict[str, float] = json.loads(profits)
        dependencies_map: Dict[str, List[str]] = json.loads(dependencies)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for profits or dependencies.")

    # temporary directory to save uploaded files
    tmpdir = tempfile.mkdtemp(prefix="jobs_")
    job_info = {}

    try:
        # Save uploaded files
        for file in files:
            filename = file.filename
            if not filename:
                raise HTTPException(status_code=400, detail="One uploaded file is missing a filename.")
            filepath = os.path.join(tmpdir, filename)
            with open(filepath, "wb") as f:
                f.write(await file.read())

            # check profit exists
            if filename not in profits_map:
                raise HTTPException(status_code=400, detail=f"Profit not provided for file '{filename}'.")

            # measure runtime safely (utils uses timeout)
            try:
                runtime_ms = measure_runtime(filepath)
            except RuntimeError as e:
                # bubble up a clean message
                raise HTTPException(status_code=400, detail=str(e))

            # store job info (runtime in ms, profit)
            job_info[filename] = {"runtime": runtime_ms, "profit": float(profits_map[filename])}

        # Validate dependency keys refer to uploaded files
        for k, deps in dependencies_map.items():
            if k not in job_info:
                raise HTTPException(status_code=400, detail=f"Dependency entry for unknown job '{k}'.")
            for d in deps:
                if d not in job_info:
                    raise HTTPException(status_code=400, detail=f"Dependency '{d}' for job '{k}' not uploaded.")

        jobs = list(job_info.keys())

        # extract chains (this can raise ValueError)
        try:
            chains = validate_and_extract_chains(jobs, dependencies_map)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        prefixes = build_prefixes(chains, job_info)

        # capacity is milliseconds (deadline provided in seconds)
        capacity = int(float(deadline) * 1000)
        if capacity < 0:
            raise HTTPException(status_code=400, detail="Deadline must be non-negative.")

        max_profit, used_time, sequence = knapsack(prefixes, capacity)

        return JSONResponse({
            "max_profit": max_profit,
            "used_time_ms": used_time,
            "sequence": sequence,
            "chains": chains,
            "job_info": job_info
        })

    finally:
        # cleanup uploaded files directory
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass


# Entry point so `python -m backend.main` works reliably
if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
