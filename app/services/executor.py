from typing import Any, Dict
from app.models.action import ActionType, CreateAlertRuleAction, QueryStatusAction, ListRulesAction, UnsupportedAction, ParsedAction
from app.models.request import CommandResponse
from app.store.memory_store import memory_store

class ActionExecutor:
    def execute(self, action: ParsedAction, understood_as: Dict[str, Any]) -> CommandResponse:
        if isinstance(action, CreateAlertRuleAction):
            rule_data = action.model_dump()
            created_rule = memory_store.add_rule(rule_data)
            return CommandResponse(
                status="success",
                understood_as=understood_as,
                executed=True,
                message="Alert rule created successfully.",
                data={"rule": created_rule}
            )

        elif isinstance(action, QueryStatusAction):
            telemetry_val = memory_store.get_telemetry(action.device_id, action.metric)
            return CommandResponse(
                status="success",
                understood_as=understood_as,
                executed=True,
                message=f"Current {action.metric} for '{action.device_id}' is {telemetry_val}.",
                data={
                    "device_id": action.device_id,
                    "metric": action.metric,
                    "value": telemetry_val
                }
            )

        elif isinstance(action, ListRulesAction):
            rules = memory_store.get_rules(action.device_id)
            return CommandResponse(
                status="success",
                understood_as=understood_as,
                executed=True,
                message=f"Retrieved {len(rules)} alert rules.",
                data={"rules": rules, "count": len(rules)}
            )

        elif isinstance(action, UnsupportedAction):
            return CommandResponse(
                status="unsupported",
                understood_as=understood_as,
                executed=False,
                message=action.reason
            )

        else:
            return CommandResponse(
                status="error",
                understood_as=understood_as,
                executed=False,
                message="Unknown action type provided to executor."
            )

executor_service = ActionExecutor()
