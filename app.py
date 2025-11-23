from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel, ValidationError
from src.tasks.solve import solve_task_with_llm

app = FastAPI()

# Define the secret that will be used for validation
SECRET_KEY = "6969"

# Define the request model
class SolveRequest(BaseModel):
    email: str
    secret: str
    url: str

@app.post("/start-solve")
async def start_solve(request: Request, background_tasks: BackgroundTasks):
    try:
        # Parse and validate the JSON payload
        body = await request.json()
        solve_request = SolveRequest(**body)
    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Validate the secret
    if solve_request.secret != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    # Add the solve_task_with_llm function to background tasks
    background_tasks.add_task(solve_quiz, solve_request.url, solve_request.email, solve_request.secret)

    # Respond immediately with success
    return {"message": "Validation successful! Starting to solve the quiz..."}

def solve_quiz(url: str, email: str, secret: str):
    print(f"[QUIZ START] Starting quiz solving for URL: {url}")
    i = 1
    while url:
        print(f"  [TASK {i}] Starting task {i}...")
        url = solve_task_with_llm(url, email, secret)
        print(f"  [TASK {i}] Task {i} completed.")
        i += 1
    print("[QUIZ END] All tasks completed.")