from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

# 1. This is what a single "Cloud Resource" looks like to the Agent
class CloudResource(BaseModel):
    id: str = Field(..., description="Unique ID of the resource")
    type: str = Field(..., description="Type: 'server', 'database', or 'storage'")
    cpu_usage: float = Field(..., description="CPU utilization percentage (0-100)")
    cost_per_hour: float = Field(..., description="Hourly cost in USD")
    is_public: bool = Field(..., description="Is this accessible to the public internet?")
    is_encrypted: bool = Field(..., description="Is the data encrypted?")

# 2. This is the "Observation" - What the agent sees at every step
class Observation(BaseModel):
    resources: List[CloudResource]
    total_monthly_cost: float
    security_score: float  # 0 to 100 based on vulnerabilities

# 3. This is the "Action" - What the agent can do
class Action(BaseModel):
    command: str = Field(..., description="Action to take: 'terminate', 'encrypt', or 'revoke_access'")
    resource_id: str = Field(..., description="The ID of the resource to act upon")

# 4. Mandatory OpenEnv Step Response Structure
# This ensures the API response is typed and validated for the grader
class StepResponse(BaseModel):
    observation: Observation
    reward: float
    terminated: bool
    truncated: bool
    info: Dict[str, Any] = Field(default_factory=dict)

# 5. This is the "Reward" object (Optional, mainly for documentation)
class Reward(BaseModel):
    reward: float = Field(..., description="The score for the last action taken")