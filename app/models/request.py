from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class CommandRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Natural language command prompt from user")

class CommandResponse(BaseModel):
    status: str = Field(..., description="Response status: 'success', 'validation_error', 'unsupported', or 'error'")
    understood_as: Dict[str, Any] = Field(..., description="Structured JSON representation extracted by LLM")
    executed: bool = Field(..., description="Whether backend successfully validated and executed the action")
    message: str = Field(..., description="Human-readable result or error message")
    data: Optional[Dict[str, Any]] = Field(None, description="Optional payload data (e.g. telemetry query results or created rule object)")
    errors: Optional[List[str]] = Field(None, description="List of specific validation errors if execution failed")

class AlertRuleResponse(BaseModel):
    id: str
    device_id: str
    metric: str
    condition: str
    threshold: float
    duration_minutes: int
    notify_via: List[str]
    created_at: str

class RulesListResponse(BaseModel):
    rules: List[AlertRuleResponse]
    total: int
