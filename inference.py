import os
import asyncio
import requests
from typing import List, Optional
from openai import OpenAI

# --- MANDATORY CONFIGURATION ---
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")

# Environment Endpoint
# NOTE: If running on HF Spaces, the validator will set ENV_URL to your Space URL
BASE_URL = os.getenv("ENV_URL", "http://localhost:8000") 

# Task Metadata
TASK_NAME = os.getenv("TASK_ID", "medium-security-sweep")
BENCHMARK = "cloud-sentinel-v1"
MAX_STEPS = 10

# --- LOGGING HELPERS (STDOUT FORMAT COMPLIANCE) ---
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action_str: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = str(error).lower() if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action_str} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

# --- LLM INTERACTION ---
SYSTEM_PROMPT = """
You are a Cloud Security Agent. Your goal is to secure the cloud environment.
Available commands: 'encrypt', 'revoke_access', 'terminate'.
You must respond with ONLY the command and the resource_id in this format:
command:resource_id
Example: encrypt:8b3f2a1c
"""

def get_agent_action(client: OpenAI, obs: dict) -> str:
    # Handle both direct obs and obs-wrapped-in-response
    resources = obs.get('resources', [])
    
    resources_summary = "\n".join([
        f"- ID: {r['id']}, Type: {r['type']}, Public: {r['is_public']}, Encrypted: {r['is_encrypted']}" 
        for r in resources
    ])
    
    user_prompt = f"Current Resources:\n{resources_summary}\n\nWhat is your next action?"
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0, # Set to 0.0 for more deterministic, reliable actions
            max_tokens=50
        )
        return (completion.choices[0].message.content or "").strip().lower()
    except Exception as e:
        return f"error:{str(e)}"

# --- MAIN EXECUTION LOOP ---
async def main():
    if not API_KEY:
        print("[ERROR] HF_TOKEN is not set. Cannot proceed with inference.")
        return

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    # Start Episode
    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
    
    rewards = []
    steps_taken = 0
    success = False
    final_score = 0.0

    try:
        # 1. Reset
        reset_resp = requests.post(f"{BASE_URL}/reset").json()
        current_obs = reset_resp
        
        for step in range(1, MAX_STEPS + 1):
            steps_taken = step
            
            # 2. Get Action from LLM
            raw_action = get_agent_action(client, current_obs)
            
            # Parse LLM response
            if ":" not in raw_action:
                log_step(step, raw_action, 0.0, False, "Invalid Format")
                continue

            try:
                cmd, r_id = raw_action.split(":", 1)
                action_payload = {"command": cmd.strip(), "resource_id": r_id.strip()}
            except:
                log_step(step, raw_action, 0.0, False, "Parse Error")
                continue

            # 3. Step the Environment
            step_resp = requests.post(f"{BASE_URL}/step", json=action_payload).json()
            
            # Update values based on StepResponse model
            current_obs = step_resp['observation']
            reward = step_resp['reward']
            terminated = step_resp['terminated']
            error = step_resp['info'].get('error')

            rewards.append(reward)
            log_step(step, raw_action, reward, terminated, error)

            if terminated:
                break
        
        # 4. Final Grading
        grader_resp = requests.get(f"{BASE_URL}/grader", params={"task_id": TASK_NAME}).json()
        final_score = grader_resp.get("score", 0.0)
        success = final_score >= 1.0  # Set threshold to 1.0 for a strict "Pass"

    except Exception as e:
        # Avoid crashing completely so we can still emit [END]
        pass
    finally:
        log_end(success=success, steps=steps_taken, score=final_score, rewards=rewards)

if __name__ == "__main__":
    asyncio.run(main())