from typing import Any, Dict, List, Optional, Tuple
from app.models.action import ActionType, CreateAlertRuleAction, QueryStatusAction, ListRulesAction, UnsupportedAction, ParsedAction
from app.store.memory_store import memory_store
from pydantic import ValidationError

class ValidationResult:
    def __init__(self, is_valid: bool, action: Optional[ParsedAction] = None, errors: Optional[List[str]] = None, message: str = ""):
        self.is_valid = is_valid
        self.action = action
        self.errors = errors or []
        self.message = message

class ActionValidator:
    def validate_action_dict(self, raw_action: Dict[str, Any]) -> ValidationResult:
        if not isinstance(raw_action, dict) or "type" not in raw_action:
            return ValidationResult(
                is_valid=False,
                errors=["Invalid LLM output format: missing 'type' field."],
                message="Structured JSON output from parser must contain an action 'type'."
            )

        action_type = raw_action.get("type")

        # 1. Pydantic Schema Validation
        try:
            if action_type == ActionType.CREATE_ALERT_RULE:
                action = CreateAlertRuleAction(**raw_action)
            elif action_type == ActionType.QUERY_STATUS:
                action = QueryStatusAction(**raw_action)
            elif action_type == ActionType.LIST_RULES:
                action = ListRulesAction(**raw_action)
            elif action_type == ActionType.UNSUPPORTED:
                action = UnsupportedAction(**raw_action)
                return ValidationResult(
                    is_valid=True,
                    action=action,
                    message=f"Action is unsupported: {action.reason}"
                )
            else:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Unknown action type '{action_type}'."],
                    message=f"Action type '{action_type}' is not recognized."
                )
        except ValidationError as ve:
            error_msgs = [f"{err['loc'][0]}: {err['msg']}" for err in ve.errors()]
            return ValidationResult(
                is_valid=False,
                errors=error_msgs,
                message="Schema validation failed for extracted action."
            )

        # 2. Device Registry & Business Rule Validation
        devices = memory_store.get_devices()
        errors = []

        if isinstance(action, CreateAlertRuleAction):
            device_id = action.device_id
            metric = action.metric

            # Check device existence in registry
            if device_id not in devices:
                available_devices = list(devices.keys())
                errors.append(f"Device '{device_id}' does not exist in registry. Registered devices: {available_devices}")
            else:
                # Check metric support for this device
                supported_metrics = devices[device_id].get("metrics", [])
                if metric not in supported_metrics:
                    errors.append(f"Device '{device_id}' does not support metric '{metric}'. Supported metrics: {supported_metrics}")

            # Business rule checks
            if action.duration_minutes <= 0:
                errors.append("duration_minutes must be greater than 0.")
            if not action.notify_via:
                errors.append("At least one notification method must be specified in notify_via.")

        elif isinstance(action, QueryStatusAction):
            device_id = action.device_id
            metric = action.metric

            if device_id not in devices:
                available_devices = list(devices.keys())
                errors.append(f"Device '{device_id}' does not exist in registry. Registered devices: {available_devices}")
            else:
                supported_metrics = devices[device_id].get("metrics", [])
                if metric not in supported_metrics:
                    errors.append(f"Device '{device_id}' does not support metric '{metric}'. Supported metrics: {supported_metrics}")

        elif isinstance(action, ListRulesAction):
            if action.device_id and action.device_id not in devices:
                available_devices = list(devices.keys())
                errors.append(f"Device '{action.device_id}' does not exist in registry. Registered devices: {available_devices}")

        if errors:
            return ValidationResult(
                is_valid=False,
                action=action,
                errors=errors,
                message="Device registry / business rule validation failed."
            )

        return ValidationResult(
            is_valid=True,
            action=action,
            message="Validation successful."
        )

validator_service = ActionValidator()
