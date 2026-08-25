from enum import Enum
from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator

class ActionType(str, Enum):
    CREATE_ALERT_RULE = "CREATE_ALERT_RULE"
    QUERY_STATUS = "QUERY_STATUS"
    LIST_RULES = "LIST_RULES"
    UNSUPPORTED = "UNSUPPORTED"

class ConditionType(str, Enum):
    ABOVE = "ABOVE"
    BELOW = "BELOW"
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"

class NotificationChannel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    SLACK = "SLACK"
    WEBHOOK = "WEBHOOK"

class BaseAction(BaseModel):
    type: ActionType

class CreateAlertRuleAction(BaseAction):
    type: Literal[ActionType.CREATE_ALERT_RULE] = ActionType.CREATE_ALERT_RULE
    device_id: str = Field(..., description="Target device identifier")
    metric: str = Field(..., description="Telemetry metric name to monitor")
    condition: ConditionType = Field(..., description="Threshold comparison operator")
    threshold: float = Field(..., description="Numerical threshold limit")
    duration_minutes: int = Field(..., gt=0, description="Duration threshold must persist in minutes")
    notify_via: List[NotificationChannel] = Field(default_factory=lambda: [NotificationChannel.EMAIL], description="Notification channels")

    @field_validator("condition", mode="before")
    def normalize_condition(cls, v):
        if isinstance(v, str):
            v_upper = v.upper()
            if v_upper in ["GREATER_THAN", "EXCEEDS", "ABOVE", ">"]:
                return ConditionType.ABOVE
            elif v_upper in ["LESS_THAN", "DROPS_BELOW", "BELOW", "<"]:
                return ConditionType.BELOW
            elif v_upper in ["EQUAL", "EQUALS", "=="]:
                return ConditionType.EQUALS
        return v

    @field_validator("notify_via", mode="before")
    def normalize_channels(cls, v):
        if isinstance(v, str):
            v = [v]
        if isinstance(v, list):
            res = []
            for item in v:
                if isinstance(item, str):
                    item_upper = item.upper()
                    if item_upper in NotificationChannel.__members__:
                        res.append(NotificationChannel[item_upper])
                    else:
                        res.append(NotificationChannel.EMAIL)
                else:
                    res.append(item)
            return res
        return v

class QueryStatusAction(BaseAction):
    type: Literal[ActionType.QUERY_STATUS] = ActionType.QUERY_STATUS
    device_id: str = Field(..., description="Target device identifier")
    metric: str = Field(..., description="Target metric name to query")

class ListRulesAction(BaseAction):
    type: Literal[ActionType.LIST_RULES] = ActionType.LIST_RULES
    device_id: Optional[str] = Field(None, description="Optional device filter")

class UnsupportedAction(BaseAction):
    type: Literal[ActionType.UNSUPPORTED] = ActionType.UNSUPPORTED
    reason: str = Field(..., description="Explanation why the requested action is unsupported")

# Union of all supported actions
ParsedAction = Union[CreateAlertRuleAction, QueryStatusAction, ListRulesAction, UnsupportedAction]
