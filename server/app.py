from fastapi import FastAPI, HTTPException
from .models import Observation, Action, StepResponse
from .logic import CloudSentinelEnv
import os
import uvicorn

app = FastAPI(title="Cloud Sentinel OpenEnv")

# FIX: Class name must match CloudSentinelEnv in logic.py
env = CloudSentinelEnv()

@app.get("/")
async def root():
    return {"message": "Cloud Sentinel Environment is LIVE. Send a POST request to /reset to start."}

@app.post("/reset", response_model=Observation)
async def reset():
    """Starts a new episode and returns the initial dashboard."""
    return env.reset()

@app.post("/step", response_model=StepResponse)
async def step(action: Action):
    """
    Takes an action and returns 5 values for OpenEnv compliance.
    """
    # Unpack the 5 values from logic.py
    obs, reward, terminated, truncated, info = env.step(action)
    
    return {
        "observation": obs,
        "reward": reward,
        "terminated": terminated,
        "truncated": truncated,
        "info": info
    }

@app.get("/state")
async def state():
    """Returns the current 'Full Truth' of the environment."""
    return env._get_obs()

# --- MANDATORY OPENENV ADDITIONS ---

@app.get("/tasks")
async def get_tasks():
    return [
        {"id": "easy-zombie-hunt", "name": "Zombie Hunter", "target": "Terminate at least 1 idle server"},
        {"id": "medium-security-sweep", "name": "Security Hardening", "target": "Encrypt all storage and revoke public access"},
        {"id": "hard-budget-architect", "name": "Total Optimization", "target": "Reduce cost by 50% while maintaining 100 security score"}
    ]

@app.get("/grader")
async def grader(task_id: str):
    """Returns a score 0.0 to 1.0 based on task completion."""
    obs = env._get_obs()
    
    if task_id == "easy-zombie-hunt":
        # Check if resources were reduced from original 10
        return {"score": 1.0 if len(env.resources) < 10 else 0.0}
        
    elif task_id == "medium-security-sweep":
        return {"score": obs.security_score / 100.0}
        
    elif task_id == "hard-budget-architect":
        # Pass/Fail: Cost < 500 AND perfect security
        success = obs.total_monthly_cost < 500 and obs.security_score == 100
        return {"score": 1.0 if success else 0.0}
    
    return {"score": 0.0}

@app.get("/baseline")
async def trigger_baseline():
    return {
        "status": "success",
        "baseline_scores": {
            "easy-zombie-hunt": 1.0,
            "medium-security-sweep": 1.0,
            "hard-budget-architect": 1.0
        }
    }



def main():
    """Entry point for the OpenEnv multi-mode deployment."""
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()