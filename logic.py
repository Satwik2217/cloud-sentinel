import uuid
import random
from models import CloudResource, Observation, Action

class CloudEnv:
    def __init__(self):
        self.resources = []
        self.reset()

    def reset(self):
        """Starts a fresh 'Cloud' with random messy resources."""
        self.resources = [
            CloudResource(
                id=str(uuid.uuid4())[:8],
                type=random.choice(["server", "database", "storage"]),
                cpu_usage=random.uniform(0, 100),
                cost_per_hour=random.uniform(0.1, 5.0),
                is_public=random.choice([True, False]),
                is_encrypted=random.choice([True, False])
            ) for _ in range(10) 
        ]
        return self._get_obs()

    def _get_obs(self):
        """Calculates the 'Dashboard' the agent sees."""
        # Standard monthly cost calculation (720 hours)
        total_cost = sum(r.cost_per_hour * 720 for r in self.resources)
        
        # Security Score: Starts at 100, drops for every public/unencrypted resource
        if not self.resources:
            security_score = 100.0
        else:
            issues = sum(1 for r in self.resources if r.is_public or not r.is_encrypted)
            # Each issue takes away from the perfect 100 score
            security_score = max(0, 100 - (issues * (100 / (len(self.resources) * 2))))
            
        return Observation(
            resources=self.resources,
            total_monthly_cost=round(total_cost, 2),
            security_score=round(security_score, 2)
        )

    def step(self, action: Action):
        """
        The core logic: Handles actions and returns 5 values for OpenEnv compliance:
        (obs, reward, terminated, truncated, info)
        """
        reward = 0.0
        terminated = False
        truncated = False # We set this to False as we handle step limits in the inference script
        info = {}
        
        # Find the target resource
        target = next((r for r in self.resources if r.id == action.resource_id), None)

        # SAFETY VALVE: If the resource ID is wrong, give a penalty
        if not target:
            return self._get_obs(), -1.0, False, False, {"error": "Invalid Resource ID"}

        # COMMAND 1: TERMINATE (The 'Zombie Hunt' Task)
        if action.command == "terminate":
            if target.cpu_usage < 10: # Success: Killed a zombie resource
                reward += 2.0 
            else: # Failure: Killed a useful production server!
                reward -= 2.5
            self.resources.remove(target)

        # COMMAND 2: ENCRYPT (The 'Security Sweep' Task)
        elif action.command == "encrypt":
            if not target.is_encrypted:
                target.is_encrypted = True
                reward += 0.5
            else:
                reward -= 0.1 # Penalty for wasting an action

        # COMMAND 3: REVOKE ACCESS (The 'Security Sweep' Task)
        elif action.command == "revoke_access":
            if target.is_public:
                target.is_public = False
                reward += 0.5
            else:
                reward -= 0.1

        # Check for 'Terminated' status (Success/Goal Reached)
        obs = self._get_obs()
        
        # Win Condition: No resources left or very high security + low cost
        if len(self.resources) == 0:
            terminated = True
        elif obs.security_score == 100 and obs.total_monthly_cost < 500:
            reward += 10.0 # Huge bonus for completing the 'Hard' task
            terminated = True

        return obs, reward, terminated, truncated, info